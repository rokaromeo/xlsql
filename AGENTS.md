# xlsql

A SQL database server written in Python that uses Excel `.xlsx` files as its storage backend. It implements the **PostgreSQL wire protocol (v3)**, so any standard PostgreSQL client library can connect to it.

**Repository:** [github.com/rokaromeo/xlsql](https://github.com/rokaromeo/xlsql)
**License:** MIT — Copyright 2026 Romeo Vegvari

---

## Project Structure

### Core Source (`xlsql/`)

| File | Lines | Purpose |
|------|------:|---------|
| `xlsql/__init__.py` | 4 | Package exports: `Database`, `Table`, `XlsxError`, `Executor`, `SQLSyntaxError` |
| `xlsql/storage.py` | 161 | `Database` and `Table` classes — manages an `.xlsx` workbook where each sheet is a table. Uses openpyxl. Thread-safe with locks. Auto-incrementing `id` column. |
| `xlsql/sql.py` | 485 | SQL tokenizer, recursive-descent parser, and `Executor` class. Supports: `CREATE TABLE`, `DROP TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE` (with `WHERE` clauses using `=`, `<>`, `>`, `<`, `>=`, `<=`, `AND`, `OR`). |
| `xlsql/protocol.py` | 320 | PostgreSQL wire protocol implementation (`PgConnection`, `PgServer`). Handles startup/auth handshake, simple query protocol, extended query protocol (Parse/Bind/Describe/Execute/Sync), SSL/GSS decline, error messages. |

### Entry Point

- **`server.py`** (63 lines) — CLI server that binds to a `host:port`, loads/creates an `.xlsx` database file, and serves SQL queries over the PostgreSQL wire protocol.

---

## Testing

### Unit Tests

- **`test/python/test_sql.py`** — pytest-based tests exercising the SQL executor directly (no network).

### Integration Tests

Six client tests that each connect to a live server over TCP port 5432 and run the same sequence of `DROP` / `CREATE` / `INSERT` / `SELECT` / `UPDATE` / `DELETE` operations:

| Language | File |
|----------|------|
| Python | `test/python/test_connect.py` |
| Node.js | `test/nodejs/test_connect.js` |
| Go | `test/go/test_connect.go` |
| Ruby | `test/ruby/connect_test.rb` |
| PHP | `test/php/test_connect.php` |
| Rust | `test/rust/src/main.rs` |

### Test Runner

- **`test.bat`** (Windows) — starts the server, waits for it to accept connections, runs all six client tests, then kills the server.

---

## CI/CD

Six GitHub Actions workflows (Python, Node.js, Go, Ruby, PHP, Rust), each:

1. Sets up Python 3.11 + installs `requirements.txt`
2. Starts `server.py` in the background on port 5432 with a per-language data file
3. Sets up the target language runtime
4. Runs the client test for that language
5. Kills the server (always, even on failure)

### Matrix Testing

| Language | Versions |
|----------|----------|
| Python | 3.9, 3.10, 3.11, 3.12 |
| Node.js | 18.x, 20.x, 22.x |
| Ruby | 3.0, 3.1, 3.2, 3.3 |

---

## Dependencies

| Language | Packages |
|----------|----------|
| Python | `openpyxl`, `psycopg`, `pytest`, `flake8` |
| Node.js | `pg` (^8.11.0) |
| Go | `github.com/jackc/pgx/v5` (v5.5.0) |
| Ruby | `pg` (~> 1.5) |
| PHP | `pgsql`, `pdo`, `pdo_pgsql` extensions (built-in PHP) |
| Rust | `tokio-postgres` (0.7), `tokio` (1, full features), `tinyvec` (=1.8.1) |

---

## Notable Details

- No `.sh` files, no `Makefile`, no `package.json` at root level.
- The `__pycache__/` in `xlsql/` contains compiled `.pyc` files for `stats.py` and `tui.py` which no longer have source files — suggesting they were deleted after compilation.
- The `test.xlsx` at root and `build/python/data.xlsx` are binary Excel files (gitignored).
