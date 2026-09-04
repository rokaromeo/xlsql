[![Python](https://github.com/rokaromeo/xlsql/actions/workflows/python-app.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/python-app.yml)
[![PHP](https://github.com/rokaromeo/xlsql/actions/workflows/php.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/php.yml)
[![Node.js](https://github.com/rokaromeo/xlsql/actions/workflows/node.js.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/node.js.yml)
[![Go](https://github.com/rokaromeo/xlsql/actions/workflows/go.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/go.yml)
[![Ruby](https://github.com/rokaromeo/xlsql/actions/workflows/ruby.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/ruby.yml)
[![Rust](https://github.com/rokaromeo/xlsql/actions/workflows/rust.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/rust.yml)

xlsql database server
=====================

It's an SQL server using Excel spreadsheets for the tables. Written in Python.

It is not meant to be used for anything, I'm just having fun and I made this.



To run:

    python server.py


The server binds by default to 127.0.0.1 port 5432 and stores files in .xlsql. These may be changed:

    python server.py --host HOST --port PORT --data DIR


DEPENDENCIES
------------

xlsql requires two Python packages:

    pip install openpyxl psycopg


SQL SUPPORT
-----------

The following statements are understood:

    CREATE TABLE name (col, col2)
    CREATE TABLE IF NOT PRESENT name (col, col2)
    DROP TABLE name
    DROP TABLE IF PRESENT name

    INSERT INTO name (c1, c2) VALUES (v1, v2)
    SELECT ... FROM name
    SELECT ... FROM name WHERE ...
    UPDATE name SET col = value [WHERE ...]
    DELETE FROM name [WHERE ...]

A WHERE clause accepts the comparison operators = <> > < >= <=, combined with AND or OR.


TESTING
-------

    python server.py              # in one terminal
    python test/python/test_connect.py  # in another

The test runs the full suite of statements over the wire and removes the data file afterwards, even if the test fails or is interrupted. It is important for me.

Client tests for the other languages live under `test/<language>` (go, nodejs, php, ruby, rust). Their dependencies (lockfiles, node_modules, bundles, vendored gems) stay in the same language folder, and any build outputs and CI data land in `build/<language>`.


BUGS
----

There are no bugs.
