The xlsql database server project
=================================



This project is just for fun. I want to see a bunch of xls files with the names of the SQL tables appear in a folder as I run a database migration and I want to open one of those xls files and see the database there normally, I want to go around and modify and see the test app SELECT result changes.

So the xlsql database would be a very simple SQL database server, but it would store the data in Microsoft Excel xls spreadsheets. For the user's perspective it would look like a normal SQL server with basic SQL commands.



Minimum features for the first major release:
=============================================

- The xlsql server would be a program I can run from the terminal.

- I could connect to it with a different program (standard SQL?).

- I want to show SQL request/response log messages in the terminal when the server is running.

- I want a separate xls file for every table.

- Only one database supported.

- Column data types are not supported, everything is a string.



- Supported DDL statements:

CREATE TABLE
DROP TABLE



- Supported DQL statements:

SELECT
INSERT
UPDATE
DELETE



I want to keep the xls files human readable/modifiable, it's just a normal xls.

The data structure of the xls files:
  - Only one sheet
  - First row is preserved for the column names
  - First column name is always "id", so the value of the cell A1 will be "id"
  - First column will be the primary key, auto increment from 1


The server creates a dir ".xlsql" where it's running, to store all those xls files.

I want a very simple PHP script to test the server's capabilities, connecting using PDO.



TODO
====

I'm dividing the project into smaller steps. These would be working versions, important milestones before the release:

- Server program runs, and it's listening on a port for incoming connections. It does not actually do anything, maybe log the connection attempts.

- Client can connect/disconnect.

- Client can run create/drop table.

- Client can run DQL commands.


