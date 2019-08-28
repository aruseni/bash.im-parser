import sqlite3

from bs4 import BeautifulSoup

from parser.const import DB_FILE
from parser.utils import (
    fetch_page,
    parse_quote,
    get_timestamp,
)


PARSING_PAGE_MESSAGE = 'Parsing page {}\n'
SKIPPING_QUOTE_MESSAGE = 'Skipping quote #{} as it is already in the DB\n'


class Parser:
    def __init__(self, start_page, end_page, stdout):
        self.start_page = start_page
        self.end_page = end_page
        self.stdout = stdout
        self.db = sqlite3.connect(DB_FILE)
        self.create_table()

    def create_table(self):
        cursor = self.db.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS quotes '
            '(id INTEGER, text TEXT, datetime INTEGER)'
        )
        self.db.commit()

    def parse_all_pages(self):
        for page_number in range(self.start_page, self.end_page+1):
            self.stdout.write(PARSING_PAGE_MESSAGE.format(page_number))
            self.parse_quotes(page_number)

    def parse_quotes(self, page_number):
        html = fetch_page(page_number)
        soup = BeautifulSoup(html, 'lxml')
        quote_articles = soup.find_all('article', class_='quote')
        for quote_article in quote_articles:
            quote = parse_quote(quote_article)
            self.write_quote(quote)

    def write_quote(self, quote):
        if self.get_count(quote['id']):
            self.stdout.write(
                SKIPPING_QUOTE_MESSAGE.format(quote['id'])
            )
            return

        timestamp = get_timestamp(quote['datetime'])

        cursor = self.db.cursor()

        cursor.execute(
            'INSERT INTO quotes (id, text, datetime) VALUES (?,?,?)',
            (quote['id'], quote['text'], timestamp)
        )

        self.db.commit()

    def get_count(self, quote_id):
        cursor = self.db.cursor()

        return cursor.execute(
            'SELECT count(*) FROM quotes WHERE id=?',
            (quote_id,)
        ).fetchone()[0]
