import os
import threading

from openpyxl import Workbook, load_workbook

ID_COLUMN = "id"
DEFAULT_SHEET = "Sheet1"


class XlsxError(Exception):
    pass


class Table:
    """One .xlsx file == one table."""

    def __init__(self, path, columns):
        self.path = path
        self.columns = columns
        self._lock = threading.Lock()

    @classmethod
    def load(cls, path):
        wb = load_workbook(path, read_only=True, data_only=True)
        ws = wb[DEFAULT_SHEET]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        if not rows:
            raise XlsxError(f"table file {path} is empty")
        columns = [str(c) for c in rows[0]]
        data = [list(r) for r in rows[1:] if any(c is not None for c in r)]
        return cls(path, columns), data

    @classmethod
    def create(cls, path, columns):
        if ID_COLUMN not in columns:
            columns = [ID_COLUMN] + columns
        wb = Workbook()
        ws = wb.active
        ws.title = DEFAULT_SHEET
        ws.append(columns)
        wb.save(path)
        wb.close()
        return cls(path, columns)

    def read_all(self):
        """Return column names and a list of row dicts."""
        with self._lock:
            _, data = Table.load(self.path)
        rows = []
        for row in data:
            d = {}
            for i, col in enumerate(self.columns):
                d[col] = row[i] if i < len(row) else None
            rows.append(d)
        return rows

    def append(self, values):
        """Append one row. values is a dict column->value. Returns new id."""
        with self._lock:
            _, data = Table.load(self.path)
            if data:
                maxid = max(int(r[0]) for r in data if r[0] is not None)
            else:
                maxid = 0
            newid = maxid + 1
            row = [newid]
            for col in self.columns[1:]:
                row.append(values.get(col))
            wb = load_workbook(self.path)
            ws = wb[DEFAULT_SHEET]
            ws.append(row)
            wb.save(self.path)
            wb.close()
        return newid

    def write_all(self, rows):
        """rows is a list of row dicts. Rewrites the whole file."""
        with self._lock:
            wb = load_workbook(self.path)
            ws = wb[DEFAULT_SHEET]
            ws.delete_rows(1, ws.max_row)
            ws.append(self.columns)
            for d in rows:
                ws.append([d.get(col) for col in self.columns])
            wb.save(self.path)
            wb.close()

    def drop(self):
        with self._lock:
            os.remove(self.path)


class Database:
    """Manages the .xlsql directory and all tables."""

    def __init__(self, dirpath):
        self.dirpath = dirpath
        self._lock = threading.RLock()
        os.makedirs(dirpath, exist_ok=True)

    def _path(self, name):
        if not self._valid_name(name):
            raise XlsxError(f"invalid table name: {name!r}")
        return os.path.join(self.dirpath, f"{name}.xlsx")

    @staticmethod
    def _valid_name(name):
        return bool(name) and all(
            c.isalnum() or c == "_" for c in name
        ) and not name.startswith(".")

    def list_tables(self):
        with self._lock:
            return sorted(
                f[:-5] for f in os.listdir(self.dirpath) if f.endswith(".xlsx")
            )

    def create_table(self, name, columns):
        with self._lock:
            path = self._path(name)
            if os.path.exists(path):
                raise XlsxError(f'table "{name}" already exists')
            Table.create(path, columns)
        return Table(self._path(name), [ID_COLUMN] + columns)

    def get_table(self, name):
        with self._lock:
            path = self._path(name)
            if not os.path.exists(path):
                raise XlsxError(f'table "{name}" does not exist')
            tbl, _ = Table.load(path)
        return tbl

    def drop_table(self, name):
        with self._lock:
            tbl = self.get_table(name)
            tbl.drop()
