from typing import List
from scraper.database import db_session
from scraper.core.models import Product
import pandas as pd
from datetime import datetime, timedelta

interval = 10


def analyze():
    """ Returns the analisis on the last fetched products.
    WARNING:The 'interval' global variable determines the time window in
    which entries uploaded to the database are consiered for this analysis."""

    products = db_session.query(Product).filter(
        Product.inserted_on > datetime.utcnow() - timedelta(minutes=interval)
    )
    total = products.count()
    new_products = products.filter(Product.is_new == True)
    total_new_products = new_products.count()
    total_new_products_with_chars, total_distinct_new_products = find_uniques(new_products)
    total_used_products = products.filter(Product.is_new == False).count()

    failed_products = len(
        [product for product in products if product.characteristics is None]
    )
    return (
        total,
        total_new_products,
        total_new_products_with_chars,
        total_distinct_new_products,
        total_used_products,
        failed_products,
    )


def find_uniques(products):
    """given a list of Products, returns the number of non duplicated chracteritics tables
    empty tables are not considered"""

    characteristics_list = []
    for product in products:
        if product.characteristics is not None:
            characteristics_list.append(product.characteristics)

    characteristics_df = pd.DataFrame(characteristics_list)
    return len(characteristics_list),len(characteristics_df.drop_duplicates().index)
