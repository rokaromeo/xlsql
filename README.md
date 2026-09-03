The xlsql database server project
=================================



This project is just for fun. I want to see a bunch of xls files with the names of the SQL tables appear in a folder as I run a database migration and I want to open one of those xls files and see the database there normally, I want to go around and modify and see the test app SELECT result changes.

So the xlsql database would be a very simple SQL database server, but it would store the data in Microsoft Excel xls spreadsheets. For the user's perspective it would look like a normal SQL server with basic SQL commands.



Features
========

- The xlsql server runs from the terminal.

- Any PostgreSQL-compatible client can connect to it (standard PostgreSQL wire protocol).

- SQL request/response log messages are shown in the terminal when the server is running.

- One separate xlsx file per table.

- Only one database supported.

- Column data types are not supported, everything is a string.



Supported DDL statements:

CREATE TABLE
DROP TABLE


Supported DQL statements:

SELECT
INSERT
UPDATE
DELETE


The xls files are human readable/modifiable, just a normal xlsx.

The data structure of the xlsx files:
  - Only one sheet
  - First row is reserved for the column names
  - First column name is always "id", so the value of the cell A1 will be "id"
  - First column is the primary key, auto increment from 1

The server creates a dir ".xlsql" where it's running, to store all those xlsx files.



How to run the server
=====================

Install dependencies:

    pip install openpyxl psycopg

Start the server (defaults to 127.0.0.1:5432, data dir .xlsql):

    python server.py

Custom host, port, and data directory:

    python server.py --host 0.0.0.0 --port 5433 --data /path/to/data



Connect with Python (psycopg)
=============================

    import psycopg

    conn = psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=test password=test")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("CREATE TABLE users (name TEXT, age INT)")
    cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    cur.execute("SELECT * FROM users")
    for row in cur.fetchall():
        print(row)

    conn.close()



Connect with PHP (PDO)
======================

    <?php
    $dsn = 'pgsql:host=127.0.0.1;port=5432;dbname=test';
    $user = 'test';
    $pass = 'test';

    $pdo = new PDO($dsn, $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $pdo->exec("CREATE TABLE users (name TEXT, age INT)");
    $pdo->exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");

    $stmt = $pdo->query("SELECT * FROM users");
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        print_r($row);
    }
    ?>



TODO
====

- Multiple database support - no, do not implement this. Ever.
- Column data types - later.
- ORDER BY / LIMIT / OFFSET - later.
- Aggregate functions - later.
- The server does not exit when I press ctrl+c in the terminal, it keeps running. I pressed the ctrl+c key combination more than two times in rapid succession. Implement a feature to gracefully quit if someone presses ctrl+c.
