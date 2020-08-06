import logging

from scraper.utils import (
    generate_urls,
    bulk_fetch_and_parse_htmls,
    fetch_and_parse_html,
)

from scraper.core.analyze import analyze
from scraper.core.models import Product, Search_page
from scraper.database import db_session, base, engine
from aiohttp.client_exceptions import ClientConnectorError
from scraper.cli import cli

import asyncio
from datetime import datetime


if __name__ == "__main__":
    start_time = datetime.now()
    base.metadata.create_all(engine)
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    
    search, pages = cli()
#    search, pages = "xiaomi", 5
    urls = generate_urls(search, pages)
    search_pages = [
        Search_page(url, page_number) for page_number, url in enumerate(urls)
    ]
    urls = [page.url for page in search_pages]
    # Requesting search pages one by one. Much better data consistency
    asyncio.run(bulk_fetch_and_parse_htmls(search_pages))
    # Requestion the url for each product found in the search page asyncronusly.
    logging.info("Asyncronusly fetching all products found in the search")
    products = []
    for page in search_pages:
        for product in page.products:
            products.append(product)

    asyncio.run(bulk_fetch_and_parse_htmls(products))
    for product in products:
        db_session.add(product)
    db_session.commit()
    elapsed_time = datetime.now() - start_time
    total, total_new, total_new_with_chars, total_new_distinct, total_used, total_failed = analyze()
    results={
'Total scraping time': elapsed_time.seconds,
'Total products expected': pages*50,
'Total products fetched': total,
'Total product tables missing':total_failed,
'Total new products': total_new,
'Total new products with characteristics': total_new_with_chars,
'Total new distinct products with characterstics': total_new_distinct,
'Total used products': total_used,
}
    for key,value in results:
        print(f'{key}: {value}')


