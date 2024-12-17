import requests
from app.utils.logger import LOG


class CrawlerSession:
    """Crawler session manager."""

    def __init__(self): ...

    def __hook_validate_response(self, res: requests.Response, *args, **kwargs) -> None:
        """Validates responses."""
        try:
            res.raise_for_status()
        except Exception as e:
            LOG.error(e)

    def create_session(self) -> requests.Session:
        """Creates requests session (with hooks)."""
        session = requests.Session()        
        hooks = [self.__hook_validate_response]
        session.hooks["response"].append(hooks)

        return session
