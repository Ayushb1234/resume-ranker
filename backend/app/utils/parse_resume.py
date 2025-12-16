import re
import uuid
from typing import Dict, List, Tuple, Any
from dateutil import parser as dateparser

# small skill list to match against - extend as needed
SKILLS = [
    "python","java","c++","c#","pytorch","tensorflow","keras","scikit-learn",
    "docker","kubernetes","aws","gcp","azure","sql","postgres","mysql",
    "nlp","computer vision","opencv","react","node.js","javascript","typescript",
    "git","linux","rest","graphql","fastapi","flask"
]

SKILL_NORMALIZE = {s.lower(): s for s in SKILLS}

VERB_PATTERNS = re.compile(r"\b(design|designed|develop|developed|implemented|built|improved|optimized|led|deployed|ship|launched|managed|created)\b", re.I)
METRIC_PATTERNS = re.compile(r"(\d+%|\d+\.\d+%|\d+\s?x|\b\d{2,}\b|\d+\.\d+|\breduced\b|\bimproved\b)", re.I)

def extract_text_sections(raw_text: str) -> Dict[str,str]:
    """
    Basic sectioning by headings heuristics.
    Returns dict like {'skills': '...', 'experience': '...', 'education': '...'}
    """
    text = raw_text
    # Normalize newlines
    text = re.sub(r"\r\n", "\n", text)
    # look for common headings
    headings = ["experience", "work experience", "professional experience", "projects", "skills",
                "education", "summary", "certifications"]
    sections = {}
    regexp = re.compile(rf"(?P<h>^({'|'.join([re.escape(h) for h in headings])})\b.*?$)", re.I | re.M)
    # find indices of headings
    matches = list(regexp.finditer(text))
    if not matches:
        # fallback: everything as 'body'
        return {"body": text}
    indices = []
    for m in matches:
        indices.append((m.start(), m.group().strip().lower()))
    # append end
    indices.append((len(text), None))
    for i in range(len(indices)-1):
        start = indices[i][0]
        end = indices[i+1][0]
        heading_text = text[start:end].strip()
        # get heading key
        hline = heading_text.splitlines()[0].lower()
        key = None
        for h in headings:
            if h in hline:
                key = h
                break
        if not key:
            key = f"section_{i}"
        sections[key] = heading_text
    return sections

def extract_skills(text: str) -> List[str]:
    found = set()
    t = text.lower()
    for s in SKILLS:
        if s.lower() in t:
            found.add(SKILL_NORMALIZE[s.lower()])
    # fuzzy: tokens that look like common patterns (e.g., torch -> pytorch)
    if "torch" in t and "pytorch" not in found:
        found.add("PyTorch")
    return sorted(list(found))

def extract_experience_bullets(text: str) -> List[Dict[str, Any]]:
    # naive bullet extraction by lines with dash or numbers
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("-") or re.match(r"^\d+\.", line) or len(line) < 400 and (VERB_PATTERNS.search(line) or METRIC_PATTERNS.search(line)):
            # quick parse duration if exists
            months = None
            # try find date ranges
            m = re.search(r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b\s*\d{2,4})\s*[-–to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\b\s*\d{2,4})", line, re.I)
            if m:
                try:
                    d1 = dateparser.parse(m.group(1))
                    d2 = dateparser.parse(m.group(2))
                    if d1 and d2:
                        months = int(abs((d2.year - d1.year) * 12 + (d2.month - d1.month)))
                except Exception:
                    months = None
            bullets.append({
                "text": line,
                "has_verb": bool(VERB_PATTERNS.search(line)),
                "has_metric": bool(METRIC_PATTERNS.search(line)),
                "duration_months": months
            })
    return bullets

def derive_experience_score(bullets: List[Dict[str, Any]]) -> float:
    if not bullets:
        return 0.0
    score = 0.0
    for b in bullets:
        s = 0.0
        if b.get("has_verb"):
            s += 0.4
        if b.get("has_metric"):
            s += 0.4
        d = b.get("duration_months")
        if d and d >= 6:
            s += 0.2
        score += min(s, 1.0)
    # average -> scale 0-100
    return round((score / len(bullets)) * 100, 2)

def derive_skill_score(found_skills: List[str], jd_skills: List[str]) -> float:
    if not jd_skills:
        return 0.0
    found = 0
    for s in jd_skills:
        if s.lower() in [x.lower() for x in found_skills]:
            found += 1
    return round((found / len(jd_skills)) * 100, 2)
