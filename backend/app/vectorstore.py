import uuid
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Any

MODEL_NAME = "all-MiniLM-L6-v2"

class FaissStore:
    def __init__(self, dim: int = 384):
        self.model = SentenceTransformer(MODEL_NAME)
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)  # inner-product; we will normalize
        self.metadatas = []  # parallel list storing metadata
        self.embeddings = []

    def _embed(self, texts: List[str]):
        embs = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embs

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        docs: list of {"id":..., "text":..., "meta":{...}}
        """
        texts = [d["text"] for d in docs]
        embs = self._embed(texts)
        self.index.add(embs.astype("float32"))
        self.embeddings.append(embs)
        for d in docs:
            self.metadatas.append(d.get("meta", {}))

    def query(self, query_text: str, top_k: int = 5):
        qemb = self._embed([query_text]).astype("float32")
        D, I = self.index.search(qemb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < len(self.metadatas):
                results.append({"score": float(score), "meta": self.metadatas[idx]})
        return results
