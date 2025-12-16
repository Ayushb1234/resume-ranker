from typing import List, Dict, Any
from .parse_resume import derive_experience_score, derive_skill_score, extract_skills
import uuid
import math

def simple_rerank(candidates: List[Dict[str, Any]], jd_text: str, top_k: int = 10, skill_vs_exp_weight: float = 0.5):
    """
    candidates: list of {
        'candidate_id':..., 'name':..., 'text': full_text, 'bullets':[], 'skills':[], 'meta':...
    }
    Returns ranked candidate list with scores and evidence.
    """
    # Extract JD skills by simple token matching against known SKILLS or by splitting
    jd_lower = jd_text.lower()
    # naive JD skills: any SKILL tokens found
    jd_skills = []
    # we import SKILLS list lazily to avoid circular import
    from .parse_resume import SKILLS
    for s in SKILLS:
        if s.lower() in jd_lower:
            jd_skills.append(s)

    results = []
    for c in candidates:
        found_skills = c.get("skills", [])
        skill_score = derive_skill_score(found_skills, jd_skills) if jd_skills else 0.0
        exp_score = derive_experience_score(c.get("bullets", []))
        overall = round(skill_vs_exp_weight * skill_score + (1 - skill_vs_exp_weight) * exp_score, 2)
        # pick evidence: top bullet (has metric) and skill occurrences
        skill_evidence = []
        for sk in found_skills:
            if sk.lower() in jd_lower or True:
                skill_evidence.append({"skill": sk, "evidence": []})
        # find top bullets
        bullets = c.get("bullets", [])
        sorted_bullets = sorted(bullets, key=lambda b: (b.get("has_metric", False), b.get("duration_months") or 0), reverse=True)
        exp_evidence = sorted_bullets[:3]
        results.append({
            "candidate_id": c.get("candidate_id"),
            "name": c.get("name"),
            "overall_score": overall,
            "skill_match_score": skill_score,
            "experience_score": exp_score,
            "matched_skills": found_skills,
            "demonstrated_experiences": exp_evidence,
            "provenance": c.get("meta"),
            "explainability": f"skill_score={skill_score}, exp_score={exp_score}"
        })
    results = sorted(results, key=lambda r: r["overall_score"], reverse=True)
    return {"job_skills": jd_skills, "results": results[:top_k]}
