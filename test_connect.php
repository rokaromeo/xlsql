<?php

$dsn = 'pgsql:host=127.0.0.1;port=5432;dbname=test';
$user = 'test';
$pass = 'test';

try {
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_TIMEOUT => 3,
    ]);
} catch (PDOException $e) {
    echo "could not connect: ", $e->getMessage(), "\n";
    exit(1);
}

$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

echo "== DROP TABLE (if present) ==\n";
try {
    $pdo->exec("DROP TABLE users");
    echo "dropped existing\n";
} catch (PDOException $e) {
    echo "none to drop\n";
}

echo "== CREATE TABLE ==\n";
$pdo->exec("CREATE TABLE users (name TEXT, age INT)");
echo "ok\n";

echo "== CREATE TABLE IF NOT PRESENT ==\n";
$pdo->exec("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)");
echo "ok\n";

echo "== INSERT ==\n";
$pdo->exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Bob', 25)");
echo "ok\n";

echo "== SELECT ==\n";
$stmt = $pdo->query("SELECT * FROM users");
foreach ($stmt as $row) {
    echo "  ";
    print_r($row);
}

echo "== SELECT WHERE ==\n";
$stmt = $pdo->query("SELECT name FROM users WHERE age > 26");
foreach ($stmt as $row) {
    echo "  ";
    print_r($row);
}

echo "== UPDATE ==\n";
$n = $pdo->exec("UPDATE users SET age = 31 WHERE name = 'Alice'");
echo "rows updated: ", $n, "\n";

echo "== SELECT AGAIN ==\n";
$stmt = $pdo->query("SELECT id, name, age FROM users");
foreach ($stmt as $row) {
    echo "  ";
    print_r($row);
}

echo "== DELETE ==\n";
$n = $pdo->exec("DELETE FROM users WHERE name = 'Bob'");
echo "rows deleted: ", $n, "\n";

echo "== DONE ==\n";
