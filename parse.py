#!/usr/bin/env python

import errno
import sys

from parser import Parser


if __name__ == '__main__':
    args_are_numbers = all(arg.isdigit() for arg in sys.argv[1:])
    if len(sys.argv) != 3 or not args_are_numbers:
        sys.stderr.write('Invalid arguments\n')
        sys.exit(errno.EINVAL)

    start_page = int(sys.argv[1])
    end_page = int(sys.argv[2])

    if end_page >= start_page > 0:
        p = Parser(start_page, end_page, sys.stdout)
        p.parse_all_pages()
    else:
        sys.stderr.write('Please check the page numbers\n')
        sys.exit(errno.EINVAL)
