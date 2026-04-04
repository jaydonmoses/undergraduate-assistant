#!/usr/bin/env python3
"""Match professor profiles against input research interests."""

import argparse
import json
import os
import sys
from typing import Dict, List, Set

# Allow imports when running the script directly from backend/.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import UndergraduateAssistantDatabase


def normalize_interest(text: str) -> str:
    """Normalize strings so matching is case-insensitive and whitespace-safe."""
    return " ".join(text.lower().strip().split())


def parse_interests(raw_interests: List[str]) -> List[str]:
    """Support either comma-separated or repeated --interest values."""
    parsed: List[str] = []
    for value in raw_interests:
        for item in value.split(","):
            clean = item.strip()
            if clean:
                parsed.append(clean)

    # Preserve order while removing duplicates.
    seen: Set[str] = set()
    deduped: List[str] = []
    for item in parsed:
        key = normalize_interest(item)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def score_professor(user_interests: List[str], professor: Dict) -> Dict:
    """Calculate a simple overlap score and keep matching labels for display."""
    prof_interests = professor.get("research_interests", []) or []
    normalized_prof = {normalize_interest(i): i for i in prof_interests if i}

    matches: List[str] = []
    for interest in user_interests:
        n_interest = normalize_interest(interest)
        if n_interest in normalized_prof:
            matches.append(normalized_prof[n_interest])
            continue

        # Secondary fuzzy condition: substring overlap either direction.
        for n_prof_interest, original in normalized_prof.items():
            if n_interest in n_prof_interest or n_prof_interest in n_interest:
                matches.append(original)
                break

    unique_matches = sorted(set(matches), key=str.lower)
    return {
        "name": professor.get("name"),
        "title": professor.get("title"),
        "position": professor.get("position"),
        "email": professor.get("email"),
        "location": professor.get("location"),
        "research_interests": prof_interests,
        "match_score": len(unique_matches),
        "matching_interests": unique_matches,
    }


def find_matches(user_interests: List[str], limit: int) -> List[Dict]:
    """Return ranked professor matches based on research-interest overlap."""
    db = UndergraduateAssistantDatabase()
    professors = db.get_all_professors()

    matches: List[Dict] = []
    for professor in professors:
        scored = score_professor(user_interests, professor)
        if scored["match_score"] > 0:
            matches.append(scored)

    matches.sort(key=lambda item: (-item["match_score"], (item.get("name") or "").lower()))
    return matches[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Match professors by research interests from the local database."
    )
    parser.add_argument(
        "--interest",
        action="append",
        required=True,
        help="Research interest(s). Use multiple flags or comma-separated values.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of matches to return (default: 10).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of a text table.",
    )
    args = parser.parse_args()

    interests = parse_interests(args.interest)
    if not interests:
        raise SystemExit("No valid research interests provided.")

    matches = find_matches(interests, max(args.limit, 1))

    if args.json:
        print(json.dumps({"input_interests": interests, "matches": matches}, indent=2))
        return

    print("Input interests:", ", ".join(interests))
    print(f"Found {len(matches)} match(es).")
    print("-" * 80)

    if not matches:
        print("No professors matched these interests. Try broader terms.")
        return

    for idx, match in enumerate(matches, start=1):
        print(f"{idx}. {match.get('name', 'Unknown')} (score: {match['match_score']})")
        if match.get("title"):
            print(f"   Title: {match['title']}")
        if match.get("position"):
            print(f"   Position: {match['position']}")
        if match.get("email"):
            print(f"   Email: {match['email']}")
        if match.get("location"):
            print(f"   Location: {match['location']}")
        print("   Matching interests:", ", ".join(match["matching_interests"]))


if __name__ == "__main__":
    main()
