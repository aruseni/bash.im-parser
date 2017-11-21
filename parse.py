#!/usr/bin/env python

import sys
import errno
import urllib2
import sqlite3
import datetime

from bs4 import BeautifulSoup

class Parser:
    db_file = "quotes.sqlite3"
    user_agent = (
        "Mozilla/5.0 "
        "(X11; Ubuntu; Linux x86_64; rv:30.0) "
        "Gecko/20100101 Firefox/30.0"
    )

    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        self.db = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS quotes "
            "(id INTEGER, text TEXT, datetime INTEGER)"
        )
        self.db.commit()

    def get_url(self, page_number):
        return "http://bash.im/index/%s" % page_number

    def fetch_page(self, page_number):
        req = urllib2.Request(
            url=self.get_url(page_number),
            headers={"User-Agent": self.user_agent}
        )
        f = urllib2.urlopen(req)
        return f.read()

    def parse_all_pages(self):
        for page_number in xrange(self.start_page, self.end_page + 1):
            self.parse_quotes(page_number)

    def parse_quotes(self, page_number):
        html = self.fetch_page(page_number)
        soup = BeautifulSoup(html, "lxml")
        quote_divs = soup.find_all("div", class_="quote")
        for quote_div in quote_divs:
            quote = {}

            text_div = quote_div.find("div", class_="text")

            # Skipping advertisement
            if not text_div:
                continue

            # The quote text divs contain strings of text and
            # <br> elements. Here all contents of a text div
            # are joined with any elements replaced by \n.
            quote["text"] = "".join(
                map(
                    lambda x: x if isinstance(x, unicode) else "\n",
                    text_div.contents
                )
            )

            quote["text"] = quote["text"].strip()

            actions_div = quote_div.find("div", class_="actions")

            quote["datetime"] = actions_div.find(
                "span",
                class_="date"
            ).contents[0]

            quote["id"] = actions_div.find(
                "a",
                class_="id"
            ).contents[0][1:]

            self.write_quote(quote)

    def write_quote(self, quote):
        cursor = self.db.cursor()

        same_id_quotes = cursor.execute(
            "SELECT * FROM quotes WHERE id=?",
            (quote["id"],)
        ).fetchall()

        if len(same_id_quotes):
            sys.stdout.write(
                "Skipping quote #%s as it is already in the DB\n"
                %
                quote["id"]
            )
            return

        dt = datetime.datetime.strptime(quote["datetime"], "%Y-%m-%d %H:%M")
        timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()

        cursor.execute(
            "INSERT INTO quotes (id, text, datetime) VALUES (?,?,?)",
            (quote["id"], quote["text"], timestamp)
        )

        self.db.commit()

if __name__ == "__main__":
    arguments = sys.argv
    if (
        len(arguments) == 3
        and arguments[1].isdigit()
        and arguments[2].isdigit()
    ):
        start_page = int(arguments[1])
        end_page = int(arguments[2])

        if start_page > 0 and end_page >= start_page:
            p = Parser(start_page, end_page)
            p.parse_all_pages()
        else:
            sys.stderr.write("Please check the page numbers\n")
            sys.exit(errno.EINVAL)
    else:
        sys.stderr.write("Invalid arguments\n")
        sys.exit(errno.EINVAL)
