"""Unit tests: Redis is mocked, so the tests run without any database."""
import unittest
from unittest.mock import patch

from redis import RedisError

import app as counter


class VisitCounterTest(unittest.TestCase):
    def setUp(self):
        self.client = counter.app.test_client()

    @patch.object(counter.redis, "incr", return_value=5)
    def test_index_shows_count_and_container_id(self, mock_incr):
        response = self.client.get("/")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cette page a été vue 5 fois", body)
        self.assertIn("Je suis le conteneur", body)
        mock_incr.assert_called_once_with("hits")

    @patch.object(counter.redis, "incr", side_effect=RedisError("down"))
    def test_index_returns_503_when_redis_is_down(self, _):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
