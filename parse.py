#!/usr/bin/env python

import datetime
import errno
import sys
import sqlite3
import urllib.request

from bs4 import BeautifulSoup, NavigableString


DB_FILE = "quotes.sqlite3"
USER_AGENT = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) "
    "Gecko/20100101 Firefox/68.0"
)


class Parser:
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.db = sqlite3.connect(DB_FILE)
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS quotes "
            "(id INTEGER, text TEXT, datetime INTEGER)"
        )
        self.db.commit()

    def get_url(self, page_number):
        return "https://bash.im/index/{}".format(page_number)

    def fetch_page(self, page_number):
        req = urllib.request.Request(
            url=self.get_url(page_number),
            headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(req) as f:
            response = f.read()
        return response

    def parse_all_pages(self):
        for page_number in range(self.start_page, self.end_page+1):
            sys.stdout.write("Parsing page {}\n".format(page_number))
            self.parse_quotes(page_number)

    def parse_quotes(self, page_number):
        html = self.fetch_page(page_number)
        soup = BeautifulSoup(html, "lxml")
        quote_articles = soup.find_all("article", class_="quote")
        for quote_article in quote_articles:
            quote = {}

            text_div = quote_article.find("div", class_="quote__body")

            quote["text"] = "\n".join(
                i.strip() for i in text_div.contents
                if isinstance(i, NavigableString) and i != "\n"
            )

            quote["id"] = quote_article.find(
                "a",
                class_="quote__header_permalink"
            ).string[1:]

            quote["datetime"] = quote_article.find(
                "div",
                class_="quote__header_date"
            ).string.strip()

            self.write_quote(quote)

    def write_quote(self, quote):
        cursor = self.db.cursor()

        count = cursor.execute(
            "SELECT count(*) FROM quotes WHERE id=?",
            (quote["id"],)
        ).fetchone()

        if count[0]:
            sys.stdout.write(
                "Skipping quote #{} as it is already in the DB\n".format(
                    quote["id"]
                )
            )
            return

        dt = datetime.datetime.strptime(
            quote["datetime"],
            "%d.%m.%Y в %H:%M"
        )
        timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()

        cursor.execute(
            "INSERT INTO quotes (id, text, datetime) VALUES (?,?,?)",
            (quote["id"], quote["text"], timestamp)
        )

        self.db.commit()


if __name__ == "__main__":
    args_are_numbers = all(arg.isdigit() for arg in sys.argv[1:])
    if len(sys.argv) != 3 or not args_are_numbers:
        sys.stderr.write("Invalid arguments\n")
        sys.exit(errno.EINVAL)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    if end_page >= start_page > 0:
        p = Parser(start_page, end_page)
        p.parse_all_pages()
    else:
        sys.stderr.write("Please check the page numbers\n")
        sys.exit(errno.EINVAL)
