import concurrent.futures as cf
from app.crawler.client import CrawlerClient
from app.crawler.session import CrawlerSession
from app.utils.file_io import parse_config
from app.utils.file_io import write_to_file
from app.utils.logger import LOG


def start_crawling(config):
    """Wrapper for crawler."""
    concurrency = config["concurrency"]
    domains = config["domains"]
    num_domains = len(domains)

    if concurrency["enabled"]:
        workers = max(concurrency["workers"], num_domains)
        LOG.info(
            f"Crawling {num_domains} domain/s concurrently with {workers} workers."
        )

        with cf.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for domain in domains:
                session = CrawlerSession()
                client = CrawlerClient(session, domain, concurrency)
                future = executor.submit(client.crawl, pages=["/"])
                futures.append(future)

            for future in cf.as_completed(futures):
                crawled = future.result()
                url = list(crawled.keys())[0]
                LOG.info(f"✅ Crawled {len(crawled[url])} pages in {url}")
                write_to_file(url, crawled)

    else:
        LOG.info(f"Crawling {num_domains} domain/s sequentially.")
        for domain in domains:
            session = CrawlerSession()
            client = CrawlerClient(session, domain)
            crawled = client.crawl(pages=["/"])
            LOG.info(
                f"✅ Crawled {len(crawled[client.base_url])} pages in {client.base_url}"
            )
            write_to_file(client.base_url, crawled)


if __name__ == "__main__":
    config = parse_config()
    start_crawling(config)
