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

### Integration Tests — Connection Tests

Six client tests that each connect to a live server over TCP port 5432 and run the same sequence of `DROP` / `CREATE` / `INSERT` / `SELECT` / `UPDATE` / `DELETE` operations:

| Language | File |
|----------|------|
| Python | `test/python/test_connect.py` |
| Node.js | `test/nodejs/test_connect.js` |
| Go | `test/go/test_connect.go` |
| Ruby | `test/ruby/connect_test.rb` |
| PHP | `test/php/test_connect.php` |
| Rust | `test/rust/src/main.rs` |

#### RULE: All Connection Tests Must Be Identical Across Languages

All connection tests across every language **must test the same things in the same order**. If you or the user adds a new test case (e.g., a new SQL statement, a new WHERE condition, a new error check) to any one language's test, you **must** immediately replicate that same test case in **all other** connection tests. Do not let a single language drift ahead of or behind the others. The purpose is to prove the server works correctly regardless of which client language connects to it.

#### What Each Connection Test Does

Every test follows the **exact same sequence** to verify the server handles the full CRUD lifecycle:

1. **Connect** to `127.0.0.1:5432` (dbname=`test`, user=`test`, password=`test`) with a 3-second timeout.
2. **DROP TABLE users** — idempotent, catches and ignores the "table does not exist" error.
3. **CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)**.
4. **INSERT 10 rows**: Alice/30, Bob/25, 4x Foo/111, 4x Bar/222.
5. **SELECT \* FROM users** — dump all rows.
6. **SELECT name FROM users WHERE age > 26** — filter test.
7. **UPDATE users SET age = 31 WHERE name = 'Alice'** — print rows affected.
8. **SELECT id, name, age FROM users** — verify the update.
9. **DELETE FROM users WHERE name = 'Bob'** — print rows deleted.
10. **SELECT \* FROM users** — final state dump.
11. **Close connection** and print `DONE`.

#### Per-Language Dependency Configs

Each language that needs external packages has a config file in its `test/<lang>/` directory:

| Language | Config File | Key Package(s) |
|----------|-------------|-----------------|
| Python | (none, uses `requirements.txt`) | `psycopg` |
| Node.js | `test/nodejs/package.json` | `pg` (^8.11.0) |
| Go | `test/go/go.mod` | `github.com/jackc/pgx/v5` (v5.5.0) |
| Ruby | `test/ruby/Gemfile` | `pg` (~> 1.5) |
| PHP | (none, uses built-in extensions) | `pgsql`, `pdo`, `pdo_pgsql` |
| Rust | `test/rust/Cargo.toml` | `tokio-postgres` (0.7), `tokio` (1, full), `tinyvec` (=1.8.1) |

---

## Running Connection Tests Locally

There are **three ways** to run all connection tests:

### 1. Windows Batch: `test.bat`

```
test.bat
```

This is the primary Windows test runner. It:
1. Deletes `build/*` and recreates `build/`.
2. Starts `server.py` with `--data build\python\data.xlsx` in the background.
3. Polls TCP port 5432 up to 30 times (1 second apart).
4. Calls each per-language `.bat` runner sequentially.
5. Kills the server and reports pass/fail.

### 2. Linux/macOS Shell: `test.sh`

```
bash test.sh
```

Same flow as `test.bat` but for Unix. Uses `nohup` for the server and a Python one-liner to poll the port.

### 3. Per-Language Runners

Each language has its own `.bat` and `.sh` runner that can be executed independently (server must already be running):

| Language | Windows | Linux/macOS |
|----------|---------|-------------|
| Python | `test_python.bat` | `test_python.sh` |
| Node.js | `test_nodejs.bat` | `test_nodejs.sh` |
| Go | `test_go.bat` | `test_go.sh` |
| Ruby | `test_ruby.bat` | `test_ruby.sh` |
| PHP | `test_php.bat` | `test_php.sh` |
| Rust | `test_rust.bat` | `test_rust.sh` |

#### Per-Language Runner Patterns

Each runner `cd`s into the language's test directory, runs the test, captures the exit code, then `cd`s back. The exit code is propagated so the master runner knows if it passed or failed.

Language-specific install steps (only run if needed):
- **Node.js**: `npm install` if `node_modules/` does not exist.
- **Ruby**: `bundle install` (via `Gemfile`).
- **Go, Rust, PHP, Python**: no install step in the runner (handled by CI or pre-installed).

---

## CI/CD — GitHub Actions

Six GitHub Actions workflows, one per language. Each workflow is a **self-contained** test: it starts its own server, runs the test, and tears down.

### Common Workflow Pattern

Every workflow follows this structure:

```yaml
# 1. Checkout code
- uses: actions/checkout@v4

# 2. Set up Python 3.11 + install dependencies
- uses: actions/setup-python@v4
  with:
    python-version: "3.11"
- run: pip install -r requirements.txt

# 3. Start xlsql server in background with per-language data file
- run: |
    python server.py --host 127.0.0.1 --port 5432 \
      --data ./build/<LANG>/data.xlsx > server.log 2>&1 &
    echo $! > server.pid
    # Poll port 5432 up to 30 times
    for i in $(seq 1 30); do
      if (echo > /dev/tcp/127.0.0.1/5432) 2>/dev/null; then break; fi
      sleep 1
    done

# 4. Set up the target language runtime
# 5. Run the client test

# 6. Kill server (always runs, even on failure)
- if: always()
  run: kill $(cat server.pid) || true
```

Key details:
- Each workflow uses its own data file path (`./build/<LANG>/data.xlsx`) to avoid file contention.
- The server PID is saved to `server.pid` and killed in the teardown step.
- The `if: always()` ensures cleanup happens even when the test fails.

### Per-Language Workflow Differences

| Language | Workflow File | Server Data Path | Extra Steps | Matrix Versions |
|----------|---------------|------------------|-------------|-----------------|
| Python | `python.yml` | `./build/python/data.xlsx` | Lint with `flake8`, run `pytest test/python/test_sql.py` | 3.9, 3.10, 3.11, 3.12 |
| Node.js | `node.js.yml` | `./build/nodejs/data.xlsx` | `npm ci` in `test/nodejs/`, `npm test` | 18.x, 20.x, 22.x |
| Go | `go.yml` | `./build/go/data.xlsx` | `go build` then run binary | (none) |
| Ruby | `ruby.yml` | `./build/ruby/data.xlsx` | `apt-get install libpq-dev`, `bundle install`, `bundle exec ruby` | 3.0, 3.1, 3.2, 3.3 |
| PHP | `php.yml` | `./build/php/data.xlsx` | `setup-php` action with extensions, `php -l` lint | (none) |
| Rust | `rust.yml` | `./build/rust/data.xlsx` | `cargo build`, `cargo run --quiet` | (none) |

### Matrix Testing

| Language | Versions |
|----------|----------|
| Python | 3.9, 3.10, 3.11, 3.12 |
| Node.js | 18.x, 20.x, 22.x |
| Ruby | 3.0, 3.1, 3.2, 3.3 |
| Go, PHP, Rust | Single version each |

---

## Adding a New Language — Step by Step

#### RULE: New Languages Must Work on All Three Platforms

When a new language is added for connection testing, it **must** run on all three platforms: GitHub Actions, Linux shell (`.sh`), and Windows batch (`.bat`). Do not add a language with only one or two runners. Always create all three: the GitHub Actions workflow, the `.sh` runner, and the `.bat` runner.

When adding a new language (e.g., Zig, Java, C#, etc.), you need to create **7 files** across 3 locations. Here is the complete checklist:

### Step 1: Create the Connection Test

Create `test/<LANG>/` directory and the test file. The test must:

- Connect to `127.0.0.1:5432` with `dbname=test`, `user=test`, `password=test`.
- Use a 3-second connection timeout.
- Run the exact same SQL sequence as all other tests (see "What Each Connection Test Does" above).
- Exit with code 0 on success, non-zero on failure.
- Print `DONE` at the end.
- Print section headers like `== DROP TABLE (if present) ==`, `== INSERT ==`, etc.

Example using Go as reference (`test/go/test_connect.go`):
```go
conn, err := pgx.Connect(ctx, "host=127.0.0.1 port=5432 dbname=test user=test password=test")
```

### Step 2: Create Dependency Config (if needed)

If the language needs a package manager config:

| Language Type | Config File |
|---------------|-------------|
| Node.js-like | `package.json` |
| Go | `go.mod` |
| Rust | `Cargo.toml` |
| Ruby | `Gemfile` |
| Python | Not needed (uses root `requirements.txt`) |
| PHP | Not needed (uses built-in extensions) |

### Step 3: Create Per-Language `.bat` Runner

Create `test_<LANG>.bat` at the project root. Template:

```batch
@echo off
setlocal

echo Running <LANG> connect tests ...
echo.

cd test\<LANG>
<run command here>
set "FAILED=%ERRORLEVEL%"
cd ..\..

echo.
if "%FAILED%"=="0" (
    echo <LANG> tests PASSED.
) else (
    echo <LANG> tests FAILED.
)

endlocal
exit /b %FAILED%
```

### Step 4: Create Per-Language `.sh` Runner

Create `test_<LANG>.sh` at the project root. Template:

```bash
#!/usr/bin/env bash

echo "Running <LANG> connect tests ..."
echo

cd test/<LANG>
<run command here>
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "<LANG> tests PASSED."
else
    echo "<LANG> tests FAILED."
fi

exit "$FAILED"
```

### Step 5: Add to Master Runners

Add a call to the new runner in both `test.bat` and `test.sh`.

**In `test.bat`**, add before the summary section:
```batch
echo --- <LANG> ---
call test_<LANG>.bat
if errorlevel 1 set "FAILED=1"
echo.
```

**In `test.sh`**, add before the summary section:
```bash
echo "--- <LANG> ---"
bash test_<LANG>.sh || FAILED=1
echo
```

### Step 6: Create GitHub Actions Workflow

Create `.github/workflows/<LANG>.yml`. Use this template (adjust the setup step and matrix as needed):

```yaml
name: <LANG>

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Start xlsql server
      run: |
        python server.py --host 127.0.0.1 --port 5432 --data ./build/<LANG>/data.xlsx > server.log 2>&1 &
        echo $! > server.pid
        for i in $(seq 1 30); do
          if (echo > /dev/tcp/127.0.0.1/5432) 2>/dev/null; then
            break
          fi
          sleep 1
        done
        if ! (echo > /dev/tcp/127.0.0.1/5432) 2>/dev/null; then
          echo "server did not start" >&2
          cat server.log >&2
          exit 1
        fi

    # TODO: Set up the target language runtime here

    # TODO: Install dependencies and/or build here

    - name: Run <LANG> client test
      # TODO: set working-directory and run command

    - name: Stop xlsql server
      if: always()
      run: |
        if [ -f server.pid ]; then
          kill $(cat server.pid) || true
        fi
```

### Step 7: Update AGENTS.md

Update the tables in this file:
- "Integration Tests" table — add the new language.
- "Per-Language Runner Patterns" table — add `.bat` and `.sh` entries.
- "Per-Language Workflow Differences" table — add the new workflow row.
- "Dependencies" table — add the new language's packages.

---

## File Inventory — Connection Test Infrastructure

```
test.bat                              Master test runner (Windows)
test.sh                               Master test runner (Linux/macOS)
test_python.bat                       Per-language runner (Windows)
test_python.sh                        Per-language runner (Linux/macOS)
test_nodejs.bat
test_nodejs.sh
test_go.bat
test_go.sh
test_ruby.bat
test_ruby.sh
test_php.bat
test_php.sh
test_rust.bat
test_rust.sh
test/python/test_connect.py           Connection test (Python)
test/python/test_sql.py               Unit test (pytest)
test/nodejs/test_connect.js           Connection test (Node.js)
test/nodejs/package.json              npm config
test/go/test_connect.go               Connection test (Go)
test/go/go.mod                        Go module config
test/ruby/connect_test.rb             Connection test (Ruby)
test/ruby/Gemfile                     Bundler config
test/php/test_connect.php             Connection test (PHP)
test/rust/src/main.rs                 Connection test (Rust)
test/rust/Cargo.toml                  Cargo config
.github/workflows/python.yml          CI workflow (Python)
.github/workflows/node.js.yml         CI workflow (Node.js)
.github/workflows/go.yml              CI workflow (Go)
.github/workflows/ruby.yml            CI workflow (Ruby)
.github/workflows/php.yml             CI workflow (PHP)
.github/workflows/rust.yml            CI workflow (Rust)
```

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

- All `.xlsx` files are gitignored — the server auto-creates them at startup if they do not exist.
- The `build/` directory is gitignored.
- The Node.js test calls `process.exit(0)` because the xlsql server never closes the TCP socket after Terminate, which would cause `client.end()` to block forever.
- The Rust test wraps everything in a 60-second `tokio::time::timeout`.
- No `.sh` files at root other than `test.sh`. No `Makefile`, no `package.json` at root level.
