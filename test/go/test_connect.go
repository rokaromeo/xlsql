package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/jackc/pgx/v5"
)

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	conn, err := pgx.Connect(ctx, "host=127.0.0.1 port=5432 dbname=test user=test password=test")
	if err != nil {
		fmt.Println("could not connect:", err)
		os.Exit(1)
	}
	defer conn.Close(ctx)

	exec := func(sql string) error {
		_, err := conn.Exec(ctx, sql)
		return err
	}

	fmt.Println("== DROP TABLE (if present) ==")
	if err := exec("DROP TABLE users"); err != nil {
		fmt.Println("none to drop")
	} else {
		fmt.Println("dropped existing")
	}

	fmt.Println("== CREATE TABLE (if not present) ==")
	exec("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)")
	fmt.Println("ok")

	fmt.Println("== INSERT ==")
	exec("INSERT INTO users (name, age) VALUES ('Alice', 30)")
	exec("INSERT INTO users (name, age) VALUES ('Bob', 25)")
	exec("INSERT INTO users (name, age) VALUES ('Foo', 111)")
	exec("INSERT INTO users (name, age) VALUES ('Foo', 111)")
	exec("INSERT INTO users (name, age) VALUES ('Foo', 111)")
	exec("INSERT INTO users (name, age) VALUES ('Foo', 111)")
	exec("INSERT INTO users (name, age) VALUES ('Bar', 222)")
	exec("INSERT INTO users (name, age) VALUES ('Bar', 222)")
	exec("INSERT INTO users (name, age) VALUES ('Bar', 222)")
	exec("INSERT INTO users (name, age) VALUES ('Bar', 222)")
	fmt.Println("ok")

	fmt.Println("== SELECT ==")
	rows, _ := conn.Query(ctx, "SELECT * FROM users")
	for rows.Next() {
		values, _ := rows.Values()
		fmt.Println(" ", values)
	}
	rows.Close()

	fmt.Println("== SELECT WHERE ==")
	rows, _ = conn.Query(ctx, "SELECT name FROM users WHERE age > 26")
	for rows.Next() {
		values, _ := rows.Values()
		fmt.Println(" ", values)
	}
	rows.Close()

	fmt.Println("== UPDATE ==")
	tag, err := conn.Exec(ctx, "UPDATE users SET age = 31 WHERE name = 'Alice'")
	if err != nil {
		fmt.Println("rows updated:", err)
	} else {
		fmt.Println("rows updated:", tag.RowsAffected())
	}

	fmt.Println("== SELECT AGAIN ==")
	rows, _ = conn.Query(ctx, "SELECT id, name, age FROM users")
	for rows.Next() {
		values, _ := rows.Values()
		fmt.Println(" ", values)
	}
	rows.Close()

	fmt.Println("== DELETE ==")
	tag, err = conn.Exec(ctx, "DELETE FROM users WHERE name = 'Bob'")
	if err != nil {
		fmt.Println("rows deleted:", err)
	} else {
		fmt.Println("rows deleted:", tag.RowsAffected())
	}

	fmt.Println("== FINAL ==")
	rows, _ = conn.Query(ctx, "SELECT * FROM users")
	for rows.Next() {
		values, _ := rows.Values()
		fmt.Println(" ", values)
	}
	rows.Close()

	conn.Close(ctx)
	fmt.Println("DONE")
}
