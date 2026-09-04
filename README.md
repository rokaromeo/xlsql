[![Python](https://github.com/rokaromeo/xlsql/actions/workflows/python.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/python.yml)
[![PHP](https://github.com/rokaromeo/xlsql/actions/workflows/php.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/php.yml)
[![Node.js](https://github.com/rokaromeo/xlsql/actions/workflows/node.js.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/node.js.yml)
[![Go](https://github.com/rokaromeo/xlsql/actions/workflows/go.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/go.yml)
[![Ruby](https://github.com/rokaromeo/xlsql/actions/workflows/ruby.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/ruby.yml)
[![Rust](https://github.com/rokaromeo/xlsql/actions/workflows/rust.yml/badge.svg)](https://github.com/rokaromeo/xlsql/actions/workflows/rust.yml)

xlsql database server
=====================

It's an SQL server using Excel spreadsheets for the tables. Written in Python.

I'm not using this software at all and you should not use it either, I'm just having fun making it. Everything about this project reminds me of what modern development became: environments, configs, setup this to work with that, package managers, update the dependencies...

It became a constant stream of failures and fixes, endless config files. Same old problems over and over again. Feels like making a lot of progress and doing a good job, but no one ever going to look at any of thism, no one wants to, but they will be forced to when it turns to shit eventually and something fails.

AI agentic coding is the solution. I really enjoy looking at it going through the hell of software development with ease. I don't want to see the contents of a yaml config file ever again in my life.

Creating automations just because humans are lazy, forget things and in general very bad when it comes to endless boring repetitive things. By now automating things is shit, boring, lots of problems, lots of the same problems, and now I know it will be like this forever, when you think you solved something, no you did not really, it just works now and it is going to fail in the future. 

Automating things sucks, but now finally we can automate it.


To run:

    python server.py


The server binds by default to 127.0.0.1 port 5432 and stores files somewhere by default. These may be changed:

    python server.py --host HOST --port PORT --data PATH


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

    python server.py                       # in one terminal
    python test/python/test_connect.py     # in another

Client tests for the other languages live under `test/<language>`. Their dependencies (lockfiles, node_modules, bundles, vendored gems) stay in their own language folder, and any build outputs and CI data land in `build/<language>`.
