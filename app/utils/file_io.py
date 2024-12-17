import yaml
import json
import re
from app.utils.logger import LOG

CONFIG_FILE = "/web_crawler/config.yml"


def parse_config(filename: str = CONFIG_FILE) -> dict:
    """Reads/parses config file."""
    try:
        with open(filename) as cfg:
            cfg_file = yaml.safe_load(cfg)
            return cfg_file

    except yaml.YAMLError as e:
        LOG.error(e)
        raise

    except Exception as e:
        LOG.error(e)
        raise


def write_to_file(domain: str, data: dict) -> str:
    """Write data for domain to file."""
    pattern = "http(s)?://(www\.)?"  # http://www. or https://www.
    stripped_domain = re.sub(pattern, "", domain)
    filename = f"{stripped_domain}.json"
    with open(filename, "w+") as f:
        data_json = json.dumps(data)
        f.write(data_json)

    LOG.info(f"Results from crawling {domain} written to {filename}")
