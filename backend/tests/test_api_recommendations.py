import os
import sys
import unittest
import asyncio

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import api.app as app_module


class TestRecommendationApi(unittest.TestCase):
    def setUp(self):
        self.original_search_users = app_module.db.search_users
        self.original_insert_user = app_module.db.insert_user
        self.original_update_user = app_module.db.update_user
        self.original_get_all_professors = app_module.db.get_all_professors

        app_module.db.search_users = lambda name=None, **kwargs: []
        app_module.db.insert_user = lambda user_data: 999
        app_module.db.update_user = lambda user_id, user_data: True
        app_module.db.get_all_professors = lambda: [
            {
                "name": "Prof ML",
                "title": "Professor",
                "position": "Khoury",
                "research_interests": ["Machine Learning", "Data Science"],
                "location": "Boston",
                "email": "ml@example.edu",
                "phone": "",
                "personal_website": "",
                "google_scholar": "",
            },
            {
                "name": "Prof Security",
                "title": "Professor",
                "position": "Khoury",
                "research_interests": ["Cybersecurity", "Privacy"],
                "location": "Boston",
                "email": "security@example.edu",
                "phone": "",
                "personal_website": "",
                "google_scholar": "",
            },
        ]

    def tearDown(self):
        app_module.db.search_users = self.original_search_users
        app_module.db.insert_user = self.original_insert_user
        app_module.db.update_user = self.original_update_user
        app_module.db.get_all_professors = self.original_get_all_professors

    def test_prof_info_returns_ranked_matches(self):
        request = app_module.ProfessorRecommendationRequest(
            user_info=app_module.UserInfo(
                name="API Test User",
                major="Data Science",
                research_interests=["Machine Learning"],
                skills=["Python"],
            )
        )

        result = asyncio.run(app_module.get_professor_recommendations(request))

        self.assertGreaterEqual(result.match_count, 1)
        top = result.recommendations[0]
        self.assertEqual(top.name, "Prof ML")
        self.assertGreater(top.match_score, 0)
        self.assertIsNotNone(top.match_reason)


if __name__ == "__main__":
    unittest.main()
