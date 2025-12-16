import os
import zipfile
import tempfile
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .schemas import RankResponse, RankRequest
from .utils.ocr_preprocess import pdf_to_images, preprocess_image
from .utils.parse_resume import extract_text_sections, extract_skills, extract_experience_bullets
from .vectorstore import FaissStore
from .utils.re_ranker import simple_rerank

app = FastAPI(title="Resume RAG + Rank Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory vector store for demo
VECTOR_STORE = FaissStore()
# simple in-memory candidate store
CANDIDATES = {}

@app.post("/rank")
async def rank_resumes(resumes_zip: UploadFile = File(...),
                       job_description: str = Form(...),
                       top_k: int = Form(10),
                       skill_vs_exp_weight: float = Form(0.5)):
    """
    Accept zip file of resumes + job_description form fields.
    Returns ranked candidates JSON.
    """
    job_id = str(uuid.uuid4())
    tmpdir = tempfile.mkdtemp(prefix="resumes_")
    try:
        # save uploaded zip
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            content = await resumes_zip.read()
            f.write(content)

        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir)

        # find files in extracted dir
        candidate_entries = []
        for root, dirs, files in os.walk(tmpdir):
            for fname in files:
                if fname.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                    path = os.path.join(root, fname)
                    # If PDF - convert pages
                    pages = []
                    if fname.lower().endswith('.pdf'):
                        pages = pdf_to_images(path)
                    else:
                        pages = [(path, 1)]

                    full_text = []
                    meta = {"file": fname, "pages": []}
                    bullets = []
                    skills = set()
                    for ppath, page_no in pages:
                        try:
                            pre = preprocess_image(ppath)
                        except Exception:
                            pre = ppath
                        # OCR - pytesseract
                        try:
                            import pytesseract
                            raw = pytesseract.image_to_string(pre)
                        except Exception as e:
                            raw = ""
                        full_text.append(raw)
                        meta["pages"].append(page_no)
                    full_text_joined = "\n".join(full_text)
                    sections = extract_text_sections(full_text_joined)
                    # skills from sections & body
                    s = set()
                    for sec_text in sections.values():
                        ss = extract_skills(sec_text)
                        s.update(ss)
                        b = extract_experience_bullets(sec_text)
                        bullets.extend(b)
                    candidate_id = str(uuid.uuid4())
                    candidate = {
                        "candidate_id": candidate_id,
                        "name": None,
                        "text": full_text_joined,
                        "bullets": bullets,
                        "skills": sorted(list(s)),
                        "meta": meta
                    }
                    CANDIDATES[candidate_id] = candidate
                    candidate_entries.append(candidate)
                    # add to vector store the full text as doc
                    VECTOR_STORE.add_documents([{"id": candidate_id, "text": full_text_joined, "meta": {"candidate_id": candidate_id, "file": fname}}])

        # run simple reranker (can be replaced by LLM-driven re-ranker)
        ranked = simple_rerank(candidate_entries, job_description, top_k=top_k, skill_vs_exp_weight=skill_vs_exp_weight)
        resp = {
            "job_id": job_id,
            "results": ranked["results"],
            "job_skills": ranked["job_skills"]
        }
        return JSONResponse(content=resp)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass

@app.get("/health")
async def health():
    return {"status": "ok"}
