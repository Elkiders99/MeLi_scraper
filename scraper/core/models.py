from typing import List
from datetime import datetime

import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from bs4.element import Tag
import unidecode
import logging
from sqlalchemy import Column, String, JSON, Boolean, Integer, DateTime, Float

from scraper.utils import fetch_html
from scraper.database import base, connection_config


class Product(base):
    """Represents a product found in a main search html"""

    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    url = Column(String(5000))
    characteristics = Column(JSON)
    is_new = Column(Boolean)
    inserted_on = Column(DateTime, default=datetime.utcnow())
    position = Column(Integer)

    def __init__(self, title: str, url: str, position: int, is_new=None):
        self.title = title
        self.url = url
        self.html = None
        self.characteristics = None
        self.is_new = is_new
        self.position = position

    def parse_html(self) -> bool:
        """ Parsers a product html and returns a boolean representing wheather 
        it was able to find everything it needed or not."""
        logging.info("parsing product html")
        soup = BeautifulSoup(self.html, "html.parser")
        table = soup.find("table", class_="andes-table")
        if table:
            rows = table.find_all("tr")
            table_data = [tuple(cell.string for cell in row) for row in rows]
            characteristics = {}
            for row in table_data:
                characteristics[row[0]] = self.pre_process_string(row[1])
            self.characteristics = characteristics
        else:
            logging.info("failed to get table,retrying")
        return table is not None  # and price is not None

    @staticmethod
    def pre_process_string(string: str) -> str:
        """Takes a string, returns a string lowercase where all it's diacritics 
        have been removed"""
        string = string.lower()
        # Removing accents
        string = unidecode.unidecode(string)
        return string


class Search_page:
    def __init__(self, url, index):
        self.url = url
        self.index = index
        self.products = None

    def parse_html(self) -> bool:
        """Parses the pages html. Returnes a boolean indicating wheather the parsing 
        was succesful or not"""
        logging.info("parsing main search")
        self.products = []
        soup = BeautifulSoup(self.html, "html.parser")
        search_list = soup.body.find("ol", id="searchResults")
        if search_list is not None:
            for position, item in enumerate(search_list.children):
                title, url = self.get_title_and_url(item)
                if url and title:
                    is_new = self.get_is_new(item)
                    position = self.index + position
                    self.products.append(
                        Product(title=title, url=url, is_new=is_new, position=position)
                    )
            return True
        else:
            logging.info("While parsing main search html failed to get main list")
            return False

    @staticmethod
    def get_title_and_url(item):
        title = None
        url = None
        if isinstance(item, Tag):
            try:
                title_container = item.h2
            except AttributeError:
                logging.info(
                    "While parsing a search HTML: Failed to fetch title container.Can't fetch any data"
                )
                title = None
                url = None
            else:
                try:
                    title = title_container.span.string
                except AttributeError as er:
                    title = None
                    logging.info("While parsing a search HTML: Failed to fetch title")
                try:
                    url = title_container.a.get("href")
                except AttributeError as er:
                    url = None
                    logging.info(
                        "While parsing a search HTML: Failed to fetch url, can't fetch any data"
                    )
        return title, url

    @staticmethod
    def get_is_new(item):
        main_div_class = item.find("div")["class"]
        if "new" in main_div_class:
            is_new = True
        elif "used" in main_div_class:
            is_new = False
        else:
            is_new = None
            logging.info(
                "While parsing search HTML: Failed to determine item's state (new or used)"
            )
        return is_new
