<?php

$dsn = 'pgsql:host=127.0.0.1;port=5432;dbname=test';
$user = 'test';
$pass = 'test';

$pdo = new PDO($dsn, $user, $pass);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$pdo->exec("CREATE TABLE users (name TEXT, age INT)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Bob', 30)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Foo', 30)");
$pdo->exec("INSERT INTO users (name, age) VALUES ('Bar', 30)");

$stmt = $pdo->query("SELECT * FROM users");
while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
    print_r($row);
}
