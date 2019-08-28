import datetime
import urllib.request

from bs4 import NavigableString

from parser.const import USER_AGENT


def get_url(page_number):
    return 'https://bash.im/index/{}'.format(page_number)


def fetch_page(page_number):
    req = urllib.request.Request(
        url=get_url(page_number),
        headers={'User-Agent': USER_AGENT}
    )

    with urllib.request.urlopen(req) as f:
        response = f.read()

    return response


def parse_quote(quote_article):
    quote = {}

    text_div = quote_article.find('div', class_='quote__body')

    quote['text'] = '\n'.join(
        i.strip() for i in text_div.contents
        if isinstance(i, NavigableString) and i != '\n'
    )

    quote['id'] = quote_article.find(
        'a',
        class_='quote__header_permalink'
    ).string[1:]

    quote['datetime'] = quote_article.find(
        'div',
        class_='quote__header_date'
    ).string.strip()

    return quote


def get_timestamp(datetime_str):
    dt = datetime.datetime.strptime(datetime_str, '%d.%m.%Y в %H:%M')
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()
