<div align="center">

# 📊 xlsql

**The SQL database that lives in your Excel spreadsheets.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](#license)

*Because running a migration and watching real `.xlsx` files appear on disk is delightful.*

</div>

---

## 🤔 Wait, what?

`xlsql` is a tiny SQL database server that stores every table as a **plain, human-readable Excel file**.

You run `CREATE TABLE users ...`, and a `users.xlsx` file magically appears in a folder. Open it in Excel, LibreOffice, or a text editor — there's your data. Edit the cell that has Alice's age, save, and the next `SELECT` picks it right up.

It speaks the **standard PostgreSQL wire protocol**, so any PostgreSQL client (`psycopg`, PDO, psql, DBeaver…) can connect and just… work.

> **The core idea:** A normal SQL server, but the storage layer is literally Excel files you can open and poke at.

---

## ✨ Features

- 🗄️ **One `.xlsx` file per table** — open any table as a real spreadsheet.
- 🔌 **PostgreSQL wire protocol** — connect with any PG-compatible client.
- 🖥️ **Runs in the terminal** — every SQL request/response is logged live.
- ✏️ **Human editable** — edit cells in Excel, see queries return new results.
- 🚦 **Graceful shutdown** — hit <kbd>Ctrl</kbd>+<kbd>C</kbd> and it exits cleanly.
- 🧠 **Tiny & dependency-light** — two packages, one module.

---

## 📚 Supported SQL

### DDL (data definition)

| Statement | Description |
|-----------|-------------|
| `CREATE TABLE name (col TEXT, col2 INT)` | Create a table. |
| `CREATE TABLE IF NOT PRESENT name (...)` | Create only if it doesn't already exist. |
| `DROP TABLE name` | Drop a table. |
| `DROP TABLE IF PRESENT name` | Drop only if it exists. |

### DML (data manipulation)

| Statement | Description |
|-----------|-------------|
| `SELECT ... FROM tbl` | Select columns / `*`. |
| `SELECT ... FROM tbl WHERE ...` | Filter with `=` `<>` `>` `<` `>=` `<=`, `AND`/`OR`. |
| `INSERT INTO tbl (c1, c2) VALUES (v1, v2)` | Insert one row. |
| `UPDATE tbl SET c = v [WHERE ...]` | Update matching rows. |
| `DELETE FROM tbl [WHERE ...]` | Delete matching rows. |

> **Not yet:** `ORDER BY`, `LIMIT`, `OFFSET`, aggregates, JOINs.
> **Never, ever:** multiple databases. One is enough. This is a *fun* project.

---

## 🗂️ How tables are stored

Each table = one `.xlsx` file in the data directory (`.xlsql` by default).

- One worksheet per file.
- **Row 1** = column names. Cell `A1` is always **`id`**.
- The `id` column is the primary key, **auto-incrementing** from 1.
- No column types — **everything is a string** (types in `CREATE` are accepted & ignored).

```
users.xlsx
┌────┬────────┬─────┐
│ id │ name   │ age │
├────┼────────┼─────┤
│ 1  │ Alice  │ 30  │
│ 2  │ Bob    │ 25  │
└────┴────────┴─────┘
```

Edit `Bob`'s age to `26` in Excel, save, and watch your `SELECT` change. 🎉

---

## 🚀 Getting started

### 1. Install

```bash
pip install openpyxl psycopg
```

### 2. Run the server

```bash
python server.py
```

Starts on `127.0.0.1:5432` and creates a `.xlsql` data folder.
Stop it anytime with <kbd>Ctrl</kbd>+<kbd>C</kbd>.

Custom host, port, or data directory:

```bash
python server.py --host 0.0.0.0 --port 5433 --data /path/to/data
```

### 3. Connect & query

**Python (`psycopg`):**

```python
import psycopg

conn = psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=test password=test")
conn.autocommit = True
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)")
cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(row)

conn.close()
```

**PHP (`PDO`):**

```php
<?php
$dsn  = 'pgsql:host=127.0.0.1;port=5432;dbname=test';
$user = 'test';
$pass = 'test';

$pdo = new PDO($dsn, $user, $pass);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$pdo->exec("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");

$stmt = $pdo->query("SELECT * FROM users");
while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
    print_r($row);
}
?>
```

Any PostgreSQL-compatible client that can do it, can do it here.

---

## 🧪 Running the tests

```bash
python server.py            # terminal 1
python test_connect.py      # terminal 2
```

The test connects over real PostgreSQL wire, runs through the DDL/DML flow, and
cleans up the `.xlsql` folder afterward (even if it fails or you quit).

---

## 🗺️ Roadmap (a.k.a. good ideas, someday)

- [x] Graceful <kbd>Ctrl</kbd>+<kbd>C</kbd> shutdown
- [x] `CREATE TABLE IF NOT PRESENT` / `DROP TABLE IF PRESENT`
- [ ] `ORDER BY`, `LIMIT`, `OFFSET`
- [ ] Aggregate functions
- [ ] Column data types
- [ ] ~~Multiple databases~~ → **never.** We said *one*. One is the fun one.

---

## 💡 Why?

Because databases are cool, Excel is familiar, and watching actual spreadsheet
files appear as you run SQL is weirdly satisfying. It's a tiny, playful project
meant to be opened, edited, and explored — not to run your bank.

---

## License

MIT — go have fun with it.

<div align="center">

**Made for the joy of watching `.xlsx` files appear.** 📂✨

</div>

