import unittest
from bs4 import BeautifulSoup
from bs4 import ResultSet
from app.crawler.client import CrawlerClient
from app.crawler.session import CrawlerSession


class TestCrawlerClient(unittest.TestCase):
    def setUp(self):
        self.domains = {
            "url": "https://random_domain.org/////",
            "sleep_duration": 5,
            "parser": "html.parser",
        }
        self.session = CrawlerSession()
        self.crawler = CrawlerClient(self.session, self.domains, concurrency=None)
        self.html_doc = """ <html>
                              <head>
                               <title>
                                The Dormouse's story
                               </title>
                              </head>
                              <body>
                               <p class="title">
                                <b>
                                 The Dormouse's story
                                </b>
                               </p>
                               <p class="story">
                                Once upon a time there were three little sisters; and their names were
                                <a class="sister" href="/elsie" id="link1">
                                 Elsie
                                </a>
                                ,
                                <a class="sister" href="/lacie" id="link2">
                                 Lacie
                                </a>
                                and
                                <a class="sister" href="https://notrandom_domain.org/tillie" id="link2">
                                 Tillie
                                </a>
                                ; and they lived at the bottom of a well.
                               </p>
                               <p class="story">
                                ...
                               </p>
                              </body>
                            </html>
                        """

    def test_strip_trailing_slash(self):
        expected_domain = "https://random_domain.org"
        given_domain = self.crawler.strip_trailing_slash(self.domains["url"])
        self.assertIsInstance(given_domain, str)
        self.assertEqual(expected_domain, given_domain)

    def test_is_subpage(self):
        subpages = ["/", "//"]
        for p in subpages:
            res = self.crawler._CrawlerClient__is_subpage(p)
            self.assertIsInstance(res, bool)
            self.assertTrue(res)

        not_subpages = ["#", "https:", "http:", "mailto:", "tel:", ".."]
        for p in not_subpages:
            res = self.crawler._CrawlerClient__is_subpage(p)
            self.assertIsInstance(res, bool)
            self.assertFalse(res)

    def test_create_fullpath(self):
        pages = ["/random_page", "random_page"]
        for p in pages:
            expected_fullpath = "https://random_domain.org/random_page"
            given_fullpath = self.crawler._CrawlerClient__create_fullpath(p)
            self.assertIsInstance(given_fullpath, str)
            self.assertEqual(expected_fullpath, given_fullpath)

    def test_get_anchors(self):
        anchors = self.crawler._CrawlerClient__get_anchors(
            BeautifulSoup(self.html_doc, self.domains["parser"])
        )
        self.assertIsInstance(anchors, ResultSet)
        self.assertEqual(len(anchors), 3)

    def test_get_hrefs(self):
        expected_hrefs = {"/elsie", "/lacie"}

        anchors = self.crawler._CrawlerClient__get_anchors(
            BeautifulSoup(self.html_doc, self.domains["parser"])
        )
        hrefs = self.crawler._CrawlerClient__get_hrefs("/", anchors)
        self.assertIsInstance(hrefs, list)
        given_hrefs = set(hrefs)
        self.assertEqual(expected_hrefs, given_hrefs)


if __name__ == "__main__":
    unittest.main()
