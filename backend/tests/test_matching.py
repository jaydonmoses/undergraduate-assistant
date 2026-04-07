import unittest
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.matching import rank_professors


class TestMatchingService(unittest.TestCase):
    def setUp(self):
        self.professors = [
            {
                "name": "Prof AI",
                "title": "Associate Professor",
                "position": "Khoury",
                "research_interests": ["Artificial Intelligence", "Machine Learning"],
                "location": "Boston",
                "email": "ai@example.edu",
                "phone": None,
                "personal_website": None,
                "google_scholar": None,
            },
            {
                "name": "Prof Systems",
                "title": "Professor",
                "position": "Khoury",
                "research_interests": ["Distributed Systems", "Operating Systems"],
                "location": "Boston",
                "email": "systems@example.edu",
                "phone": None,
                "personal_website": None,
                "google_scholar": None,
            },
            {
                "name": "Prof HCI",
                "title": "Assistant Professor",
                "position": "Khoury",
                "research_interests": ["Human Computer Interaction", "Accessibility"],
                "location": "Seattle",
                "email": "hci@example.edu",
                "phone": None,
                "personal_website": None,
                "google_scholar": None,
            },
        ]

    def test_ranks_by_interest_overlap(self):
        user = {
            "major": "Computer Science",
            "research_interests": ["machine learning"],
            "skills": [],
        }

        results = rank_professors(user, self.professors, top_k=3)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Prof AI")
        self.assertGreater(results[0]["match_score"], 0)

    def test_applies_min_score_filter(self):
        user = {
            "major": "Computer Science",
            "research_interests": ["machine learning"],
            "skills": [],
        }

        strict_results = rank_professors(
            user,
            self.professors,
            top_k=3,
            min_score=100.0,
            allow_fallback=False,
        )

        self.assertEqual(strict_results, [])

    def test_fallback_returns_best_when_threshold_too_high(self):
        user = {
            "major": "Computer Science",
            "research_interests": ["machine learning"],
            "skills": [],
        }

        fallback_results = rank_professors(
            user,
            self.professors,
            top_k=2,
            min_score=100.0,
            allow_fallback=True,
        )

        self.assertGreaterEqual(len(fallback_results), 1)
        self.assertLessEqual(len(fallback_results), 2)
        self.assertEqual(fallback_results[0]["name"], "Prof AI")

    def test_synonym_normalization_ai(self):
        user = {
            "major": "Other",
            "research_interests": ["AI"],
            "skills": [],
        }

        results = rank_professors(user, self.professors, top_k=3)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Prof AI")


if __name__ == "__main__":
    unittest.main()
