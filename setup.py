#!/usr/bin/env python2.7

import os
import sqlite3
import sys

SCHEMA_FILE = 'schema.sql'
DB_FILE = 'chess.db'


def main():
    check_if_db_exists(DB_FILE)
    schema = get_schema(SCHEMA_FILE)

    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()
    cursor.executescript(schema)


def check_if_db_exists(filename):
    if os.path.isfile(filename):
        print >> sys.stderr, 'Database already exists!'
        sys.exit(1)


def get_schema(filename):
    with open(filename, 'rU') as f:
        return f.read()


if __name__ == '__main__':
    main()
