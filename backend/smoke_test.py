#!/usr/bin/env python3
"""Deployment smoke test for Undergraduate Assistant API."""

import argparse
import json
import sys
from typing import Any, Dict, List

import requests


def _build_base_url(raw_base_url: str) -> str:
    return raw_base_url.rstrip("/")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _print_json(title: str, payload: Dict[str, Any]) -> None:
    print(f"\n{title}")
    print(json.dumps(payload, indent=2))


def run_smoke_test(base_url: str, timeout: int) -> None:
    base_url = _build_base_url(base_url)
    print(f"Running smoke test against: {base_url}")

    health_response = requests.get(f"{base_url}/health", timeout=timeout)
    _assert(health_response.status_code == 200, f"/health returned {health_response.status_code}")
    health_data = health_response.json()
    _assert(health_data.get("status") == "healthy", "Health status was not 'healthy'")
    _print_json("Health response", health_data)

    payload = {
        "user_info": {
            "name": "Smoke Test User",
            "major": "Computer Science",
            "research_interests": ["machine learning", "computer vision"],
            "skills": ["python", "pytorch"],
        }
    }
    recommendations_response = requests.post(
        f"{base_url}/prof_info",
        json=payload,
        timeout=timeout,
    )
    _assert(
        recommendations_response.status_code == 200,
        f"/prof_info returned {recommendations_response.status_code}",
    )

    recommendation_data = recommendations_response.json()
    _assert("recommendations" in recommendation_data, "Missing 'recommendations' in /prof_info response")
    _assert("match_count" in recommendation_data, "Missing 'match_count' in /prof_info response")

    recommendations: List[Dict[str, Any]] = recommendation_data.get("recommendations", [])
    _assert(len(recommendations) > 0, "No recommendations returned")

    top = recommendations[0]
    _assert(top.get("name"), "Top recommendation missing 'name'")
    _assert("match_score" in top, "Top recommendation missing 'match_score'")
    _assert(top.get("match_score", 0) > 0, "Top recommendation match_score must be > 0")
    _assert("match_reason" in top, "Top recommendation missing 'match_reason'")

    print("\nRecommendation summary")
    print(f"match_count: {recommendation_data.get('match_count')}")
    print(f"top_name: {top.get('name')}")
    print(f"top_score: {top.get('match_score')}")
    print(f"top_reason: {top.get('match_reason')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a deployed Undergraduate Assistant API")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base URL, for example https://your-app.up.railway.app",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="HTTP timeout in seconds for each request",
    )
    args = parser.parse_args()

    try:
        run_smoke_test(args.base_url, args.timeout)
    except Exception as exc:
        print(f"\nSMOKE TEST FAILED: {exc}")
        return 1

    print("\nSMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())