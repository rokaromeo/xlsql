import argparse
import os
import sys

from xlsql.protocol import PgServer
from xlsql.sql import Executor, SQLSyntaxError
from xlsql.storage import Database, XlsxError


def main():
    parser = argparse.ArgumentParser(prog="xlsql", description="xlsql database server")
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5432, help="bind port (default 5432)")
    parser.add_argument("--data", default=".xlsql", help="data directory (default .xlsql)")
    args = parser.parse_args()

    db = Database(args.data)
    executor = Executor(db)

    def log(msg):
        print(f"[{os.getpid()}] {msg}", flush=True)

    def on_query(sql):
        return executor.execute(sql)

    log(f"xlsql server starting on {args.host}:{args.port}, data dir: {os.path.abspath(args.data)}")
    log(f"tables found: {db.list_tables() or 'none'}")

    server = PgServer(args.host, args.port, on_query, logger=log)
    log("ready for connections")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("shutting down")
    return 0


if __name__ == "__main__":
    sys.exit(main())
