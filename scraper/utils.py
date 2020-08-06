from typing import List, Tuple
import logging
import asyncio
from asyncio import TimeoutError
from aiohttp import ClientSession, ClientTimeout, TCPConnector
import aiohttp
from bs4 import BeautifulSoup

from scraper.database import connection_config


def generate_urls(search_item: str, pages: int) -> List[str]:
    """Given a desired search and an amount of pages to be fetched,
    returns the list of needed urls to perform that search."""

    base = f"https://listado.mercadolibre.com.ar/{search_item}"
    urls = [base + f"/_Desde_{50*i+1}" for i in range(pages)]
    return urls


async def fetch_html(url: str, session) -> str:
    """GET request wrapper to fetch page HTML."""
    try:
        resp = await session.request(method="GET", url=url)
        html = await resp.text()
        return html
    except TimeoutError as er:
        logging.info(
            f"Failed to fetch {url} due to timeout. You might need to set a higher timeout config. URL will be requested again"
            ""
        )
    except aiohttp.ClientError as er:
        # No logro importar los errores de aiohttp. Lo mejor que encontre fue esto. https://github.com/aio-libs/aiohttp/issues/1753
        logging.info(f"Failed to fetch {url}. Falling back to request loop")


async def bulk_fetch_and_parse_htmls(pages: List) -> None:
    tasks = []
    timeout = ClientTimeout(connection_config["timeout"])
    conn = TCPConnector(limit=connection_config["parallel_max"])
    async with ClientSession(timeout=timeout, connector=conn) as session:
        for page in pages:
            tasks.append(fetch_and_parse_html(page, session))
        await asyncio.gather(*tasks)


async def fetch_and_parse_html(page, session) -> None:
    """Attempts to fetch a Product html and parse it for interesting data.
    Should it fail to either fetch the html or parse all the data it will retry a fixed amount 
    of times. Page must have a url attribute and a parse_html method"""
    for i in range(connection_config["retries"]):
        page.html = await fetch_html(page.url, session)
        if page.html is not None:
            status_ok = page.parse_html()
            if status_ok:
                # deleating self.html since it is no longer needed to reduce memory usage
                return
    delattr(page, "html")
    logging.warning(
        f"""After requesting {page.url} {connection_config['retries']} times: Failed to parse every requiered element. 
Running the scraper with a higher retry config might help. Also check your parsers!"""
    )
