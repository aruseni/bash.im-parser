bash.im parser
==============

A piece of software for fetching the quotes from bash.im.

*Usage*

    ./parse.py [start_page] [end_page]

*Example*

    ./parse.py 1 10

The quotes are added into an SQLite database. The table is called “quote” and contains 3 fields:

* id (INTEGER)
* text (TEXT)
* datetime (INTEGER)

The date and time is stored as Unix Time.

If the DB file (quotes.sqlite3) does not exist, it is created. Same applies for the table as well.

When a quote is parsed, it is only added to the DB if there is no other quote with the same ID. Otherwise the quote is skipped.
