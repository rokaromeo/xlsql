import sys

import psycopg

try:
    conn = psycopg.connect(
        "host=127.0.0.1 port=5432 dbname=test user=test password=test",
        connect_timeout=3,
    )
except psycopg.Error as e:
    print(f"could not connect: {e}")
    sys.exit(1)
conn.autocommit = True
cur = conn.cursor()

print("== DROP TABLE (if present) ==")
try:
    cur.execute("DROP TABLE users")
    print("dropped existing")
except psycopg.errors.SyntaxError:
    print("none to drop")

print("== CREATE TABLE (if not present) ==")
cur.execute("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)")
print("ok")

print("== INSERT ==")
cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
cur.execute("INSERT INTO users (name, age) VALUES ('Foo', 111)")
cur.execute("INSERT INTO users (name, age) VALUES ('Foo', 111)")
cur.execute("INSERT INTO users (name, age) VALUES ('Foo', 111)")
cur.execute("INSERT INTO users (name, age) VALUES ('Foo', 111)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bar', 222)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bar', 222)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bar', 222)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bar', 222)")
print("ok")

print("== SELECT ==")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(" ", row)

print("== SELECT WHERE ==")
cur.execute("SELECT name FROM users WHERE age > 26")
for row in cur.fetchall():
    print(" ", row)

print("== UPDATE ==")
cur.execute("UPDATE users SET age = 31 WHERE name = 'Alice'")
print("rows updated:", cur.rowcount)

print("== SELECT AGAIN ==")
cur.execute("SELECT id, name, age FROM users")
for row in cur.fetchall():
    print(" ", row)

print("== DELETE ==")
cur.execute("DELETE FROM users WHERE name = 'Bob'")
print("rows deleted:", cur.rowcount)

print("== SELECT AGAIN ==")
cur.execute("SELECT id, name, age FROM users WHERE name = 'Bob'")
rows = cur.fetchall()
print("  expected 0 rows, got", len(rows))
assert len(rows) == 0

print("== FINAL ==")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(" ", row)

conn.close()
print("DONE")
