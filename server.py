import argparse
import os
import signal
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
        result = executor.execute(sql)
        kind = result[0]
        if kind == "select":
            _, columns, rows = result
            return {"kind": "select", "columns": columns, "rows": rows}
        if kind == "create":
            return {"kind": "create", "name": result[1], "created": result[2]}
        if kind == "drop":
            return {"kind": "drop", "name": result[1], "dropped": result[2]}
        if kind == "insert":
            return {"kind": "insert", "newid": result[1]}
        if kind == "update":
            return {"kind": "update", "changed": result[1]}
        if kind == "delete":
            return {"kind": "delete", "deleted": result[1]}
        if kind == "noop":
            return {"kind": "noop"}
        raise SQLSyntaxError(f"unsupported result kind: {kind}")

    log(f"xlsql server starting on {args.host}:{args.port}, data dir: {os.path.abspath(args.data)}")
    log(f"tables found: {db.list_tables() or 'none'}")

    server = PgServer(args.host, args.port, on_query, logger=log)

    def handle_sigint(signum, frame):
        log("shutting down")
        server.shutdown()

    signal.signal(signal.SIGINT, handle_sigint)

    log("ready for connections")
    server.serve_forever()
    log("shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
