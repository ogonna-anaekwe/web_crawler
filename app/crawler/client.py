import re
import time
from typing import Any
from threading import Lock
from bs4 import BeautifulSoup
from bs4 import ResultSet
from app.utils.status_codes import StatusCodes
from app.utils.logger import LOG


class CrawlerClient:
    """Client for web crawling (pages in a single domain)."""

    def __init__(self, session, domain, concurrency=None):
        self.concurrency = concurrency
        self.domain = domain
        self.base_url = CrawlerClient.strip_trailing_slash(self.domain["url"])
        self.sleep_duration = self.domain["sleep_duration"]
        self.parser = self.domain["parser"]
        self.session = session.create_session()
        self.pages = {self.base_url: {}}  # base_url -> pages -> subpages
        self.lock = Lock()

    @staticmethod
    def strip_trailing_slash(base_url: str) -> str:
        """Strips trailing slashes from base url."""
        pattern = "(/)*$"
        stripped_base_url = re.sub(pattern, "", base_url)
        return stripped_base_url

    def __is_subpage(self, href: str) -> bool:
        """Determines if href is a subpage."""
        patterns = {
            "same_page": "#",
            "external_page": "(http(s)?:)",
            "dot_dot": "\.\.",
            "contact": "(mailto|tel):",
        }
        pattern = f"{patterns['same_page']}|{patterns['external_page']}|{patterns['dot_dot']}|{patterns['contact']}"
        same_or_external = re.match(pattern, href, re.IGNORECASE)
        is_subpage = href.startswith("/") or not same_or_external
        return is_subpage

    def __is_crawled(self, page: str) -> bool:
        """Determines if the page has been crawled. Makes the crawler acyclic."""
        return self.pages[self.base_url].get(page) is not None

    def __update(self, page: str, href: str) -> None:
        """Adds hrefs to list of hrefs found in a page."""
        is_first_page = self.pages[self.base_url].get(page) is None
        if is_first_page:
            self.pages[self.base_url][page] = [href]
        else:
            self.pages[self.base_url][page].append(href)

    def __update_pages(self, page: str, href: str) -> None:
        """Adds href to list of hrefs found in a page. This operation is thread-safe/atomic."""
        concurrency_enabled = (
            self.concurrency is not None and self.concurrency["enabled"]
        )
        if concurrency_enabled:
            with self.lock:  # will cause a slight performance hit; accuracy over speed!
                self.__update(page, href)

        else:
            self.__update(page, href)

    def __create_fullpath(self, page: str) -> str:
        """Create fullpath to page."""
        if not page.startswith("/"):
            page = f"/{page}"

        fullpath = f"{self.base_url}{page}"
        return fullpath

    def __get_html(self, page: str) -> tuple[BeautifulSoup, int]:
        """Obtains HTML content from the URL given by fullpath."""
        with self.session as s:
            fullpath = self.__create_fullpath(page)
            LOG.info(f"Crawling {fullpath}")

            res = s.get(fullpath)
            html = BeautifulSoup(res.text, self.parser)
            return html, res.status_code

    def __get_anchors(self, html: BeautifulSoup) -> ResultSet[Any]:
        """Obtains all anchor tags in the HTML document."""
        anchors = html.find_all("a")
        return anchors

    def __get_hrefs(self, page: str, anchors: ResultSet[Any]) -> list[str]:
        """Obtains all hrefs in the anchor tags in the page."""
        hrefs = []
        for anchor in anchors:
            href = anchor.get("href")
            missing_href = href is None
            if missing_href:
                continue

            if self.__is_subpage(href):
                href_exists = href in hrefs
                same_page = href == page
                if href_exists or same_page:
                    continue

                hrefs.append(href)
                self.__update_pages(page, href)

        return hrefs

    def crawl(self, pages: list[str], requeue=True, recursive=True) -> dict[str, dict]:
        """Recursively crawls pages; making sure to avoid cyclic crawling. Requeues pages for recrawling in the event of rate limits."""
        while len(pages) > 0:
            page = pages.pop(0)  # leads to the base case in the recursion
            if self.__is_crawled(page):
                continue

            html, status_code = self.__get_html(page)
            rate_limit_reached = status_code == StatusCodes.TOO_MANY_REQUESTS

            if requeue and rate_limit_reached:
                LOG.warning(
                    f"Status Code {status_code}. Requeuing page {page} due to Rate Limit.\n"
                )
                pages.append(page)  # re-try crawl later
                time.sleep(self.sleep_duration)  # mitigate 429s
                continue

            not_found = status_code == StatusCodes.NOT_FOUND
            if not_found:
                LOG.warning(f"Status Code {status_code}. {self.base_url}{page} not found")
                continue

            anchors = self.__get_anchors(html)
            hrefs = self.__get_hrefs(page, anchors)

            if recursive:
                self.crawl(hrefs)

        return self.pages
