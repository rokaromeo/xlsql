const { Client } = require('pg');

const client = new Client({
    host: '127.0.0.1',
    port: 5432,
    database: 'test',
    user: 'test',
    password: 'test',
    connectionTimeoutMillis: 3000,
});

(async () => {
    try {
        await client.connect();
    } catch (e) {
        console.log(`could not connect: ${e.message}`);
        process.exit(1);
    }

    const exec = async (sql) => {
        const res = await client.query(sql);
        return res;
    };

    console.log('== DROP TABLE (if present) ==');
    try {
        await exec('DROP TABLE users');
        console.log('dropped existing');
    } catch (e) {
        console.log('none to drop');
    }

    console.log('== CREATE TABLE (if not present) ==');
    await exec('CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)');
    console.log('ok');

    console.log('== INSERT ==');
    await exec("INSERT INTO users (name, age) VALUES ('Alice', 30)");
    await exec("INSERT INTO users (name, age) VALUES ('Bob', 25)");
    await exec("INSERT INTO users (name, age) VALUES ('Foo', 111)");
    await exec("INSERT INTO users (name, age) VALUES ('Foo', 111)");
    await exec("INSERT INTO users (name, age) VALUES ('Foo', 111)");
    await exec("INSERT INTO users (name, age) VALUES ('Foo', 111)");
    await exec("INSERT INTO users (name, age) VALUES ('Bar', 222)");
    await exec("INSERT INTO users (name, age) VALUES ('Bar', 222)");
    await exec("INSERT INTO users (name, age) VALUES ('Bar', 222)");
    await exec("INSERT INTO users (name, age) VALUES ('Bar', 222)");
    console.log('ok');

    console.log('== SELECT ==');
    let res = await exec('SELECT * FROM users');
    for (const row of res.rows) {
        console.log(' ', row);
    }

    console.log('== SELECT WHERE ==');
    res = await exec("SELECT name FROM users WHERE age > 26");
    for (const row of res.rows) {
        console.log(' ', row);
    }

    console.log('== UPDATE ==');
    res = await exec("UPDATE users SET age = 31 WHERE name = 'Alice'");
    console.log('rows updated:', res.rowCount);

    console.log('== SELECT AGAIN ==');
    res = await exec('SELECT id, name, age FROM users');
    for (const row of res.rows) {
        console.log(' ', row);
    }

    console.log('== DELETE ==');
    res = await exec("DELETE FROM users WHERE name = 'Bob'");
    console.log('rows deleted:', res.rowCount);

    console.log('== FINAL ==');
    res = await exec('SELECT * FROM users');
    for (const row of res.rows) {
        console.log(' ', row);
    }

    await client.end();
    console.log('DONE');
})();
