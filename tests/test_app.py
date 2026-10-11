import unittest

from app import app, find_best_faq


class FaqChatbotTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_matches_shipping_question(self):
        result = find_best_faq("When will my package arrive?")
        self.assertTrue(result["matched"])
        self.assertEqual(result["category"], "Shipping")
        self.assertIn("3–5 business days", result["answer"])

    def test_matches_return_question(self):
        response = self.client.post("/api/chat", json={"question": "Can I get a refund?"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["matched"])
        self.assertEqual(response.get_json()["category"], "Returns")

    def test_unmatched_question_returns_suggestions(self):
        result = find_best_faq("What is the weather on Mars today?")
        self.assertFalse(result["matched"])
        self.assertTrue(result["suggestions"])

    def test_rejects_non_text_question(self):
        response = self.client.post("/api/chat", json={"question": 42})
        self.assertEqual(response.status_code, 400)

    def test_rejects_oversized_question(self):
        response = self.client.post("/api/chat", json={"question": "a" * 501})
        self.assertEqual(response.status_code, 400)

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"How can we help?", response.data)


if __name__ == "__main__":
    unittest.main()
