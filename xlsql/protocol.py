import socket
import struct
import threading

from .sql import summarize


class WireError(Exception):
    pass


class PgConnection:
    """Handles the PostgreSQL v3 wire protocol for one client socket."""

    def __init__(self, sock, logger=None, on_query=None, on_terminate=None,
                 server_version="14.0", server_encoding="UTF8"):
        self.sock = sock
        self.logger = logger
        self.on_query = on_query
        self.on_terminate = on_terminate
        self.server_version = server_version
        self.server_encoding = server_encoding

    # -- low level io ---------------------------------------------------
    def send_message(self, msg_type, payload=b""):
        if msg_type is not None:
            header = struct.pack("!BI", ord(msg_type), len(payload) + 4)
        else:
            header = struct.pack("!I", len(payload) + 4)
        self.sock.sendall(header + payload)

    def recv_bytes(self, n):
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                raise WireError("client disconnected")
            data += chunk
        return data

    def recv_message(self):
        msg_type = self.recv_bytes(1)
        (length,) = struct.unpack("!I", self.recv_bytes(4))
        body = self.recv_bytes(length - 4)
        return msg_type, body

    # -- payload builders ----------------------------------------------
    @staticmethod
    def cstring(s):
        return s.encode("utf-8") + b"\x00"

    @staticmethod
    def build_auth_ok():
        return struct.pack("!I", 0)

    @staticmethod
    def build_parameter_status(name, value):
        return PgConnection.cstring(name) + PgConnection.cstring(value)

    @staticmethod
    def build_backend_key(pid, key):
        return struct.pack("!II", pid, key)

    @staticmethod
    def build_row_description(columns):
        payload = struct.pack("!H", len(columns))
        for name in columns:
            payload += PgConnection.cstring(name)
            # table oid, attr num, type oid, typlen, typmod, format
            payload += struct.pack("!IhIhih", 0, 0, 25, -1, -1, 0)
        return payload

    @staticmethod
    def build_data_row(values):
        payload = struct.pack("!H", len(values))
        for v in values:
            if v is None:
                payload += struct.pack("!i", -1)
            else:
                b = str(v).encode("utf-8")
                payload += struct.pack("!i", len(b)) + b
        return payload

    @staticmethod
    def build_command_complete(tag):
        return PgConnection.cstring(tag)

    @staticmethod
    def build_error(severity, code, message):
        fields = [
            (b"S", severity.encode("utf-8")),
            (b"C", code.encode("utf-8")),
            (b"M", message.encode("utf-8")),
        ]
        payload = b""
        for kind, val in fields:
            payload += kind + val + b"\x00"
        payload += b"\x00"
        return payload

    def send_error(self, code, message, severity="ERROR"):
        self.send_message("E", self.build_error(severity, code, message))

    def send_ready(self):
        self.send_message("Z", b"I")

    # -- startup / main loop -------------------------------------------
    def handle(self):
        try:
            self._startup()
        except (WireError, OSError):
            return
        try:
            self._main_loop()
        except (WireError, OSError):
            pass
        finally:
            if self.on_terminate:
                self.on_terminate()

    def _startup(self):
        # Loop to handle SSLRequest / GSSENCRequest before the real startup message.
        # Special codes:
        #   80877103 = SSLRequest, 80877102 = CancelRequest, 80877104 = GSSENCRequest
        while True:
            len_bytes = self.recv_bytes(4)
            (total_len,) = struct.unpack("!I", len_bytes)
            body = self.recv_bytes(total_len - 4)
            version = struct.unpack("!I", body[:4])[0] if len(body) >= 4 else 0
            if version == 80877103 or version == 80877104:
                # decline SSL / GSS encryption
                self.sock.sendall(b"N")
                continue
            if version == 80877102:
                return
            protocol = (version >> 16) & 0xFFFF
            if protocol != 3:
                raise WireError(f"unsupported protocol version {protocol}")
            # real startup message; ignore the parameter list
            break
        self._send_startup_ok()

    def _send_startup_ok(self):
        self.send_message("R", self.build_auth_ok())
        for name, value in (("server_version", self.server_version),
                            ("server_encoding", self.server_encoding),
                            ("client_encoding", self.server_encoding),
                            ("integer_datetimes", "on"),
                            ("DateStyle", "ISO, MDY")):
            self.send_message("S", self.build_parameter_status(name, value))
        self.send_message("K", self.build_backend_key(1, 2))
        self.send_ready()

    def _main_loop(self):
        self._stmt_result = None
        self._stmt_error = False
        while True:
            msg_type, body = self.recv_message()
            if msg_type == b"Q":
                self._handle_query(body)
            elif msg_type == b"X":
                return
            elif msg_type == b"P":
                self._handle_parse(body)
            elif msg_type == b"B":
                self._handle_bind()
            elif msg_type == b"D":
                self._handle_describe(body)
            elif msg_type == b"E":
                self._handle_execute()
            elif msg_type == b"S":
                # in extended protocol, errors are reset at Sync
                self._stmt_error = False
                self.send_ready()
            elif msg_type == b"C":
                pass  # Close - nothing to close
            else:
                if self.logger:
                    self.logger(f"ignoring message type {msg_type!r}")

    def _handle_parse(self, body):
        # [stmt_name\0][query\0][int16 nparams][oid...]
        parts = body.split(b"\x00", 2)
        if len(parts) < 2:
            self._fail_parse("malformed parse message")
            return
        sql = parts[1].decode("utf-8").strip()
        self.log_sql(sql)
        try:
            self._stmt_result = self.on_query(sql)
        except Exception as e:
            self.log("ERROR", str(e))
            self._fail_parse(f"{type(e).__name__}: {e}")
            return
        self._stmt_error = False
        self.send_message("1", b"")  # ParseComplete
        # ParameterDescription: int16 nparams followed by one oid per param
        if len(parts) >= 3 and len(parts[2]) >= 2:
            nparams = struct.unpack("!H", parts[2][0:2])[0]
        else:
            nparams = 0
        self.send_message("t", struct.pack("!H", nparams))

    def _fail_parse(self, message):
        self._stmt_error = True
        self._stmt_result = None
        self.send_error("42601", message)

    def _handle_bind(self):
        if self._stmt_error:
            return
        if self._stmt_result is None:
            return
        self.send_message("2", b"")  # BindComplete

    def _handle_describe(self, body):
        # [b'P'|b'S'][name\0]
        if self._stmt_error:
            return
        if self._stmt_result is None:
            return
        if self._stmt_result["kind"] == "select":
            self.send_message("T", self.build_row_description(self._stmt_result["columns"]))
        else:
            self.send_message("n", b"")  # NoData

    def _handle_execute(self):
        if self._stmt_error:
            return
        if self._stmt_result is None:
            return
        result = self._stmt_result
        if result["kind"] == "select":
            for row in result["rows"]:
                self.send_message("D", self.build_data_row(row))
            self.send_message("C", self.build_command_complete(f"SELECT {len(result['rows'])}"))
        else:
            self.send_message("C", self._command_tag(result))

    def _handle_query(self, body):
        sql = body.rstrip(b"\x00").decode("utf-8").strip()
        self.log_sql(sql)
        try:
            result = self.on_query(sql)
        except Exception as e:
            self.log("ERROR", str(e))
            self.send_error("42601", f"{type(e).__name__}: {e}")
            self.send_ready()
            return
        self._send_result(result, sql)
        self.send_ready()

    def _command_tag(self, result):
        kind = result["kind"]
        if kind == "create":
            name = result["name"]
            created = result.get("created", True)
            return f"CREATE TABLE {name}" if created else f"CREATE TABLE {name} (skipped, already present)"
        if kind == "drop":
            name = result["name"]
            dropped = result.get("dropped", True)
            return f"DROP TABLE {name}" if dropped else f"DROP TABLE {name} (skipped, not present)"
        if kind == "insert":
            return "INSERT 0 1"
        if kind == "update":
            return f"UPDATE {result['changed']}"
        if kind == "delete":
            return f"DELETE {result['deleted']}"
        if kind == "noop":
            return "OK"
        return "OK"

    def _send_result(self, result, sql):
        kind = result["kind"]
        if kind == "select":
            columns = result["columns"]
            rows = result["rows"]
            self.send_message("T", self.build_row_description(columns))
            for row in rows:
                self.send_message("D", self.build_data_row(row))
            self.send_message("C", self.build_command_complete(f"SELECT {len(rows)}"))
        else:
            self.send_message("C", self.build_command_complete(self._command_tag(result)))

    def log(self, tag, msg):
        if self.logger:
            self.logger(f"[{tag}] {msg}")

    def log_sql(self, sql):
        if self.logger:
            self.logger(f"[SQL] {summarize(sql)}")


class PgServer:
    def __init__(self, host, port, on_query, logger=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.host = host
        self.port = port
        self.on_query = on_query
        self.logger = logger
        self._shutdown = threading.Event()

    def shutdown(self):
        self._shutdown.set()

    def serve_forever(self):
        self.sock.settimeout(1.0)
        try:
            while not self._shutdown.is_set():
                try:
                    conn, addr = self.sock.accept()
                except socket.timeout:
                    continue
                if self.logger:
                    self.logger(f"[CONNECT] {addr[0]}:{addr[1]}")
                c = PgConnection(conn, logger=self.logger, on_query=self.on_query)
                self._handle_conn(c, addr)
        finally:
            self.sock.close()

    def _handle_conn(self, conn_obj, addr):
        t = threading.Thread(target=conn_obj.handle, daemon=True)
        t.start()
