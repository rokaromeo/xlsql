#!/usr/bin/env ruby
# frozen_string_literal: true

require 'pg'

begin
  conn = PG.connect(
    host: '127.0.0.1',
    port: 5432,
    dbname: 'test',
    user: 'test',
    password: 'test',
    connect_timeout: 3
  )
rescue PG::Error => e
  puts "could not connect: #{e.message}"
  exit 1
end

def exec_all(conn, sql)
  conn.exec(sql)
rescue PG::Error
  nil
end

puts '== DROP TABLE (if present) =='
begin
  conn.exec('DROP TABLE users')
  puts 'dropped existing'
rescue PG::Error
  puts 'none to drop'
end

puts '== CREATE TABLE (if not present) =='
exec_all(conn, 'CREATE TABLE IF NOT PRESENT users (name TEXT, age INT)')
puts 'ok'

puts '== INSERT =='
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Alice', 30)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Bob', 25)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Foo', 111)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Foo', 111)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Foo', 111)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Foo', 111)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Bar', 222)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Bar', 222)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Bar', 222)")
exec_all(conn, "INSERT INTO users (name, age) VALUES ('Bar', 222)")
puts 'ok'

puts '== SELECT =='
conn.exec('SELECT * FROM users') do |result|
  result.each { |row| puts "  #{row}" }
end

puts '== SELECT WHERE =='
conn.exec('SELECT name FROM users WHERE age > 26') do |result|
  result.each { |row| puts "  #{row}" }
end

puts '== UPDATE =='
result = conn.exec("UPDATE users SET age = 31 WHERE name = 'Alice'")
puts "rows updated: #{result.cmd_tuples}"

puts '== SELECT AGAIN =='
conn.exec('SELECT id, name, age FROM users') do |result|
  result.each { |row| puts "  #{row}" }
end

puts '== DELETE =='
result = conn.exec("DELETE FROM users WHERE name = 'Bob'")
puts "rows deleted: #{result.cmd_tuples}"

puts '== FINAL =='
conn.exec('SELECT * FROM users') do |result|
  result.each { |row| puts "  #{row}" }
end

conn.close
puts 'DONE'
