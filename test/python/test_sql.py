import os
import tempfile

import pytest

from xlsql.sql import Executor, SQLSyntaxError
from xlsql.storage import Database


@pytest.fixture
def db():
    path = os.path.join(tempfile.mkdtemp(), "data.xlsx")
    d = Database(path)
    yield Executor(d)


def test_create_table(db):
    result = db.execute("CREATE TABLE users (name TEXT, age INT)")
    assert result[0] == "create"
    assert result[1] == "users"
    assert result[2] is True


def test_insert_and_select(db):
    db.execute("CREATE TABLE users (name TEXT, age INT)")
    db.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    db.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")

    kind, columns, rows = db.execute("SELECT * FROM users")
    assert kind == "select"
    assert columns == ["id", "name", "age"]
    assert len(rows) == 2
    assert rows[0] == [1, "Alice", "30"]
    assert rows[1] == [2, "Bob", "25"]


def test_select_where(db):
    db.execute("CREATE TABLE users (name TEXT, age INT)")
    db.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    db.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")

    kind, columns, rows = db.execute("SELECT name FROM users WHERE age > 26")
    assert kind == "select"
    assert columns == ["name"]
    assert len(rows) == 1
    assert rows[0] == ["Alice"]


def test_update(db):
    db.execute("CREATE TABLE users (name TEXT, age INT)")
    db.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")

    kind, changed = db.execute("UPDATE users SET age = 31 WHERE name = 'Alice'")
    assert kind == "update"
    assert changed == 1

    _, _, rows = db.execute("SELECT age FROM users")
    assert rows[0] == ["31"]


def test_delete(db):
    db.execute("CREATE TABLE users (name TEXT, age INT)")
    db.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    db.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")

    kind, deleted = db.execute("DELETE FROM users WHERE name = 'Bob'")
    assert kind == "delete"
    assert deleted == 1

    _, _, rows = db.execute("SELECT name FROM users")
    assert len(rows) == 1


def test_drop_table(db):
    db.execute("CREATE TABLE users (name TEXT, age INT)")
    kind, name, dropped = db.execute("DROP TABLE users")
    assert kind == "drop"
    assert name == "users"
    assert dropped is True


def test_unknown_statement_raises(db):
    with pytest.raises(SQLSyntaxError):
        db.execute("CREATE DATABASE foo")
