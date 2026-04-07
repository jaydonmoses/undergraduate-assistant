import re
from typing import Dict, List, Set, Tuple


SYNONYM_MAP = {
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "nlp": "natural language processing",
    "hci": "human computer interaction",
    "cv": "computer vision",
    "infosec": "cybersecurity",
    "security": "cybersecurity",
    "data sci": "data science",
    "compilers": "programming languages",
}


MAJOR_KEYWORDS = {
    "computer science": {
        "software engineering",
        "programming languages",
        "systems",
        "algorithms",
        "distributed systems",
        "operating systems",
    },
    "data science": {
        "data science",
        "machine learning",
        "statistics",
        "data mining",
        "artificial intelligence",
    },
    "information systems": {
        "information systems",
        "databases",
        "human computer interaction",
        "software engineering",
    },
    "cybersecurity": {
        "cybersecurity",
        "cryptography",
        "network security",
        "privacy",
    },
    "computer engineering": {
        "computer architecture",
        "embedded systems",
        "robotics",
        "systems",
    },
    "game design": {
        "graphics",
        "human computer interaction",
        "virtual reality",
        "machine learning",
    },
    "human-computer interaction": {
        "human computer interaction",
        "user experience",
        "design",
        "accessibility",
    },
    "artificial intelligence": {
        "artificial intelligence",
        "machine learning",
        "natural language processing",
        "computer vision",
        "robotics",
    },
}


def _normalize_text(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9\s\-]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return SYNONYM_MAP.get(value, value)


def _normalize_terms(values: List[str]) -> Set[str]:
    normalized = set()
    for raw in values or []:
        clean = _normalize_text(raw)
        if clean:
            normalized.add(clean)
    return normalized


def _extract_professor_terms(professor: Dict) -> Set[str]:
    fields = [
        professor.get("title", ""),
        professor.get("position", ""),
        professor.get("location", ""),
    ]

    terms = _normalize_terms(professor.get("research_interests", []))

    for field in fields:
        clean_field = _normalize_text(field)
        if clean_field:
            terms.add(clean_field)
            for token in clean_field.split():
                if len(token) > 2:
                    terms.add(token)

    return terms


def rank_professors(
    user_info: Dict,
    professors: List[Dict],
    top_k: int = 20,
    min_score: float = 0.0,
    allow_fallback: bool = True,
) -> List[Dict]:
    user_interests = _normalize_terms(user_info.get("research_interests", []))
    user_skills = _normalize_terms(user_info.get("skills", []))
    user_major = _normalize_text(user_info.get("major", ""))
    major_terms = MAJOR_KEYWORDS.get(user_major, set())

    ranked: List[Tuple[float, Dict]] = []

    for professor in professors:
        prof_terms = _extract_professor_terms(professor)

        interest_matches = sorted(user_interests & prof_terms)
        skill_matches = sorted(user_skills & prof_terms)
        major_matches = sorted(major_terms & prof_terms)

        score = 0.0
        score += len(interest_matches) * 5.0
        score += len(skill_matches) * 3.0
        score += len(major_matches) * 2.0

        if score <= 0:
            continue

        reasons = []
        if interest_matches:
            reasons.append(
                "Interest overlap: " + ", ".join(interest_matches[:3])
            )
        if skill_matches:
            reasons.append("Skill alignment: " + ", ".join(skill_matches[:3]))
        if major_matches:
            reasons.append("Major alignment: " + ", ".join(major_matches[:3]))

        ranked_professor = dict(professor)
        ranked_professor["match_score"] = round(score, 2)
        ranked_professor["match_reason"] = " | ".join(reasons)
        ranked.append((score, ranked_professor))

    ranked.sort(key=lambda item: (item[0], item[1].get("name", "")), reverse=True)

    filtered = [prof for score, prof in ranked if score >= min_score]
    if filtered:
        return filtered[:top_k]

    if allow_fallback:
        return [prof for _, prof in ranked[:top_k]]

    return []