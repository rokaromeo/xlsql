import psycopg

conn = psycopg.connect(
    "host=127.0.0.1 port=5432 dbname=test user=test password=test",
    connect_timeout=3,
)
conn.autocommit = True
cur = conn.cursor()

print("== DROP TABLE (if present) ==")
try:
    cur.execute("DROP TABLE users")
    print("dropped existing")
except psycopg.errors.SyntaxError:
    print("none to drop")

print("== CREATE TABLE ==")
cur.execute("CREATE TABLE users (name TEXT, age INT)")
print("ok")

print("== INSERT ==")
cur.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
cur.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
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

print("== FINAL ==")
cur.execute("SELECT * FROM users")
for row in cur.fetchall():
    print(" ", row)

conn.close()
print("DONE")
