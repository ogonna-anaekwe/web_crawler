import unittest
import requests
from app.crawler.session import CrawlerSession


class TestCrawlerSession(unittest.TestCase):
    def setUp(self):
        self.url = ("https://random_domain.org",)
        self.session = CrawlerSession()

    def test_create_session(self):
        sess = self.session.create_session()
        self.assertIsInstance(sess, requests.Session)
        self.assertIsNotNone(sess)

        expected_hooks = {"response"}
        given_hooks = set(sess.hooks.keys())
        self.assertEqual(given_hooks, expected_hooks)
        self.assertEqual(len(sess.hooks.values()), 1)


if __name__ == "__main__":
    unittest.main()
