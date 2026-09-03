import tempfile, os
from xlsql.storage import Database
from xlsql.sql import Executor

d = Database(tempfile.mkdtemp())
e = Executor(d)

print(e.execute("CREATE TABLE users (name VARCHAR, age INT)"))
print(e.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)"))
print(e.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)"))
print(e.execute("SELECT name, age FROM users"))
print(e.execute("SELECT name FROM users WHERE age > 26"))
print("tables:", list(d.list_tables()))
print(e.execute("UPDATE users SET age = 31 WHERE name = 'Alice'"))
print(e.execute("SELECT * FROM users"))
print(e.execute("DELETE FROM users WHERE name = 'Bob'"))
print(e.execute("SELECT * FROM users"))
