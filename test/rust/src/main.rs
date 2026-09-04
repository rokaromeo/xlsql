use std::time::Duration;

use tokio_postgres::NoTls;
use tokio_postgres::SimpleQueryMessage;

async fn dump(client: &tokio_postgres::Client, sql: &str) {
    let messages = client
        .simple_query(sql)
        .await
        .expect("query failed");
    let mut columns: Vec<String> = Vec::new();
    for message in &messages {
        match message {
            SimpleQueryMessage::Row(row) => {
                if columns.is_empty() {
                    columns = row.columns().iter().map(|c| c.name().to_string()).collect();
                    println!("  {}", columns.join(" | "));
                }
                let values: Vec<&str> = row
                    .columns()
                    .iter()
                    .map(|c| row.get(c.name()).unwrap_or("NULL"))
                    .collect();
                println!("  {}", values.join(" | "));
            }
            SimpleQueryMessage::CommandComplete(tag) => {
                let _ = tag;
            }
            _ => {}
        }
    }
}

async fn exec(client: &tokio_postgres::Client, sql: &str) {
    let _ = client.simple_query(sql).await.unwrap();
}

#[tokio::main]
async fn main() {
    let (client, connection) = match tokio_postgres::connect(
        "host=127.0.0.1 port=5432 dbname=test user=test password=test",
        NoTls,
    )
    .await
    {
        Ok(pair) => pair,
        Err(e) => {
            println!("could not connect: {}", e);
            std::process::exit(1);
        }
    };

    tokio::spawn(async move {
        if let Err(e) = connection.await {
            eprintln!("connection error: {}", e);
        }
    });

    let _ = tokio::time::timeout(Duration::from_secs(60), async {
        println!("== DROP TABLE (if present) ==");
        match client.simple_query("DROP TABLE users").await {
            Ok(_) => println!("dropped existing"),
            Err(_) => println!("none to drop"),
        }

        println!("== CREATE TABLE (if not present) ==");
        exec(&client, "CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)").await;
        println!("ok");

        println!("== INSERT ==");
        exec(&client, "INSERT INTO users (name, age) VALUES ('Alice', 30)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Bob', 25)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Foo', 111)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Foo', 111)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Foo', 111)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Foo', 111)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Bar', 222)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Bar', 222)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Bar', 222)").await;
        exec(&client, "INSERT INTO users (name, age) VALUES ('Bar', 222)").await;
        println!("ok");

        println!("== SELECT ==");
        dump(&client, "SELECT * FROM users").await;

        println!("== SELECT WHERE ==");
        dump(&client, "SELECT name FROM users WHERE age > 26").await;

        println!("== UPDATE ==");
        let messages = client
            .simple_query("UPDATE users SET age = 31 WHERE name = 'Alice'")
            .await
            .unwrap();
        for message in messages {
            if let SimpleQueryMessage::CommandComplete(n) = message {
                println!("rows updated: {}", n);
            }
        }

        println!("== SELECT AGAIN ==");
        dump(&client, "SELECT id, name, age FROM users").await;

        println!("== DELETE ==");
        let messages = client
            .simple_query("DELETE FROM users WHERE name = 'Bob'")
            .await
            .unwrap();
        for message in messages {
            if let SimpleQueryMessage::CommandComplete(n) = message {
                println!("rows deleted: {}", n);
            }
        }

        println!("== SELECT AGAIN ==");
        let messages = client
            .simple_query("SELECT id, name, age FROM users WHERE name = 'Bob'")
            .await
            .unwrap();
        let mut count = 0;
        for message in &messages {
            if let SimpleQueryMessage::Row(_) = message {
                count += 1;
            }
        }
        println!("  expected 0 rows, got {}", count);
        assert_eq!(count, 0);

        println!("== FINAL ==");
        dump(&client, "SELECT * FROM users").await;
    })
    .await
    .unwrap();

    println!("DONE");
}
