import unittest

from app.utils.file_io import parse_config
from app.utils.file_io import CONFIG_FILE


class TestParseConfig(unittest.TestCase):
    def setUp(self):
        self.cfg = parse_config(CONFIG_FILE)

    def test_parse_config(self):
        self.assertIsInstance(self.cfg, dict)

        expected_params = {"concurrency", "domains"}
        given_params = set(self.cfg.keys())
        self.assertEqual(expected_params, given_params)

        expected_concurrency_params = {"enabled", "workers"}
        given_concurrency_params = set(self.cfg["concurrency"].keys())
        self.assertEqual(expected_concurrency_params, given_concurrency_params)

        for v in self.cfg["concurrency"].values():
            self.assertIsNotNone(v)

        for domain in self.cfg["domains"]:
            self.assertIsNotNone(domain.get("url"))
            self.assertIsNotNone(domain.get("sleep_duration"))
            self.assertIsNotNone(domain.get("parser"))


if __name__ == "__main__":
    unittest.main()
