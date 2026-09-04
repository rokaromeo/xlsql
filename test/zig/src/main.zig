const std = @import("std");
const pg = @import("pg");

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;

    var conn = pg.Conn.open(io, allocator, .{
        .host = "127.0.0.1",
        .port = 5432,
    }) catch |err| {
        std.debug.print("could not connect: {}\n", .{err});
        std.process.exit(1);
    };
    defer conn.deinit();

    conn.auth(.{
        .username = "test",
        .password = "test",
        .database = "test",
        .timeout = 3_000,
    }) catch |err| {
        std.debug.print("could not connect: {}\n", .{err});
        std.process.exit(1);
    };

    std.debug.print("== DROP TABLE (if present) ==\n", .{});
    _ = conn.exec("DROP TABLE users", .{}) catch {
        std.debug.print("none to drop\n", .{});
    };

    std.debug.print("== CREATE TABLE (if not present) ==\n", .{});
    _ = try conn.exec("CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)", .{});
    std.debug.print("ok\n", .{});

    std.debug.print("== INSERT ==\n", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Alice', 30)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Bob', 25)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Foo', 111)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Foo', 111)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Foo', 111)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Foo', 111)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Bar', 222)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Bar', 222)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Bar', 222)", .{});
    _ = try conn.exec("INSERT INTO users (name, age) VALUES ('Bar', 222)", .{});
    std.debug.print("ok\n", .{});

    std.debug.print("== SELECT ==\n", .{});
    try dump(&conn, "SELECT * FROM users");

    std.debug.print("== SELECT WHERE ==\n", .{});
    try dump(&conn, "SELECT name FROM users WHERE age > 26");

    std.debug.print("== UPDATE ==\n", .{});
    try dumpWithRowsAffected(&conn, "UPDATE users SET age = 31 WHERE name = 'Alice'");

    std.debug.print("== SELECT AGAIN ==\n", .{});
    try dump(&conn, "SELECT id, name, age FROM users");

    std.debug.print("== DELETE ==\n", .{});
    try dumpWithRowsAffected(&conn, "DELETE FROM users WHERE name = 'Bob'");

    std.debug.print("== FINAL ==\n", .{});
    try dump(&conn, "SELECT * FROM users");

    std.debug.print("DONE\n", .{});
}

fn dump(conn: *pg.Conn, sql: []const u8) !void {
    var result = try conn.query(sql, .{});
    defer result.deinit();

    while (try result.next()) |row| {
        std.debug.print("  ", .{});
        for (row.values, 0..) |value, col| {
            if (col > 0) std.debug.print(" | ", .{});
            if (value.is_null) {
                std.debug.print("NULL", .{});
            } else {
                std.debug.print("{s}", .{value.data});
            }
        }
        std.debug.print("\n", .{});
    }
}

fn dumpWithRowsAffected(conn: *pg.Conn, sql: []const u8) !void {
    const rows = (try conn.exec(sql, .{})) orelse 0;
    if (std.mem.startsWith(u8, sql, "UPDATE ")) {
        std.debug.print("  rows updated: {d}\n", .{rows});
    } else if (std.mem.startsWith(u8, sql, "DELETE ")) {
        std.debug.print("  rows deleted: {d}\n", .{rows});
    }
}
