# xlsql

PostgreSQL wire protocol server using Excel `.xlsx` files as storage. MIT License.

## Core Source

| File | Purpose |
|------|---------|
| `xlsql/storage.py` | `Database` and `Table` classes — manages `.xlsx` workbook (openpyxl, thread-safe, auto-incrementing `id`). |
| `xlsql/sql.py` | Tokenizer, recursive-descent parser, `Executor`. Supports CREATE/DROP TABLE, INSERT, SELECT, UPDATE, DELETE with WHERE (=, <>, >, <, >=, <=, AND, OR). |
| `xlsql/protocol.py` | PostgreSQL v3 wire protocol (`PgConnection`, `PgServer`). Auth handshake, simple/extended query protocol. |
| `server.py` | CLI entry point — binds host:port, loads `.xlsx` file, serves SQL. |

## Testing

Unit tests: `test/python/test_sql.py` (pytest, no network).

Connection tests: six languages, same SQL sequence each:

| Language | File |
|----------|------|
| Python | `test/python/test_connect.py` |
| Node.js | `test/nodejs/test_connect.js` |
| Go | `test/go/test_connect.go` |
| Ruby | `test/ruby/connect_test.rb` |
| PHP | `test/php/test_connect.php` |
| Rust | `test/rust/src/main.rs` |

### Test Sequence (all languages identical)

Connect to `127.0.0.1:5432` (dbname=test, user=test, password=test, 3s timeout), then:
1. DROP TABLE users (ignore "does not exist" error)
2. CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)
3. INSERT 10 rows: Alice/30, Bob/25, 4x Foo/111, 4x Bar/222
4. SELECT * FROM users
5. SELECT name FROM users WHERE age > 26
6. UPDATE users SET age = 31 WHERE name = 'Alice' — print rows affected
7. SELECT id, name, age FROM users
8. DELETE FROM users WHERE name = 'Bob' — print rows deleted
9. SELECT * FROM users
10. Close, print DONE

---

## GLOBAL RULES

1. **Rule priority:** Lower number first. Complete one fully before starting the next.
2. **Step order:** Follow steps numerically. Parallel only if no conflicts.

### RULE #1: All Connection Tests Must Be Identical

**Trigger:** User asks to add/change/remove a test case in any connection test file.

**Rule:** All connection tests must test the same things in the same order. Replicate any change across all six languages immediately.

**Steps:**
BEFORE 1: Track what worked, quirks, and tips for the next agent.
1. Read the modified test.
2. Read all other connection test files.
3. Implement the same test case in all other languages at the same position.
4. Use the same section headers, SQL statements, and values across all languages.
5. Never skip a language.

AFTER 1: Update this rule's steps if you found a better way.
AFTER 2: Update README.md if badges/docs are affected.

### RULE #2: New Languages Must Work on All Three Platforms

**Trigger:** User asks to add a new language for connection testing.

**Rule:** Must create all three: GitHub Actions workflow, `.sh` runner, and `.bat` runner. Never add a language with only partial coverage.

**Steps (7 files across 3 locations):**
BEFORE 1: Track what worked and quirks.
1. Create `test/<LANG>/` with the connection test (same SQL sequence as above, exit 0 on success, print DONE).
2. Create dependency config if needed (`package.json`, `go.mod`, `Cargo.toml`, `Gemfile` — Python/PHP don't need one).
3. Create `test_<LANG>.bat` at root (cd into dir, run, capture exit code, cd back, report pass/fail).
4. Create `test_<LANG>.sh` at root (same pattern for bash).
5. Add calls to both `test.bat` and `test.sh`.
6. Create `.github/workflows/<LANG>.yml` (checkout, Python 3.11 + requirements.txt, start server with `--data ./build/<LANG>/data.xlsx`, poll port 5432, setup target lang, run test, kill server with `if: always()`).
7. Update all relevant tables in this file.

AFTER 1: Improve this rule's steps if needed.
AFTER 2: Update README.md.

---

## Per-Language Config

| Language | Config File | Package(s) |
|----------|-------------|------------|
| Python | `requirements.txt` (root) | `openpyxl`, `psycopg`, `pytest`, `flake8` |
| Node.js | `test/nodejs/package.json` | `pg` (^8.11.0) |
| Go | `test/go/go.mod` | `github.com/jackc/pgx/v5` (v5.5.0) |
| Ruby | `test/ruby/Gemfile` | `pg` (~> 1.5) |
| PHP | (built-in) | `pgsql`, `pdo`, `pdo_pgsql` |
| Rust | `test/rust/Cargo.toml` | `tokio-postgres` (0.7), `tokio` (1, full), `tinyvec` (=1.8.1) |

## CI Matrix

| Language | Versions |
|----------|----------|
| Python | 3.9, 3.10, 3.11, 3.12 |
| Node.js | 18.x, 20.x, 22.x |
| Ruby | 3.0, 3.1, 3.2, 3.3 |
| Go, PHP, Rust | Single version |

## Notable Details

- `.xlsx` files and `build/` are gitignored; server auto-creates them.
- Node.js test calls `process.exit(0)` because xlsql never closes TCP after Terminate.
- Rust test wraps in 60-second `tokio::time::timeout`.
- Master runners: `test.bat` (Windows) and `test.sh` (Linux/macOS). Per-language runners: `test_<LANG>.bat` / `test_<LANG>.sh`.
