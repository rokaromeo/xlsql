import re
import json

from .storage import ID_COLUMN, XlsxError


class SQLSyntaxError(Exception):
    pass


TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
  | (?P<string>'(?:[^']|'')*')
  | (?P<number>\d+(?:\.\d+)?)
  | (?P<ident>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<op>[()=,<>\*])
    """,
    re.VERBOSE,
)


def tokenize(sql):
    tokens = []
    pos = 0
    n = len(sql)
    while pos < n:
        m = TOKEN_RE.match(sql, pos)
        if not m:
            raise SQLSyntaxError(f"unexpected character at position {pos}: {sql[pos]!r}")
        pos = m.end()
        if m.lastgroup == "ws":
            continue
        if m.lastgroup == "string":
            val = m.group().strip("'").replace("''", "'")
            tokens.append(("STRING", val))
        elif m.lastgroup == "number":
            text = m.group()
            tokens.append(("NUMBER", float(text) if "." in text else int(text)))
        else:
            tokens.append((m.lastgroup.upper(), m.group().casefold() if m.lastgroup == "ident" else m.group()))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self, offset=0):
        j = self.i + offset
        if j < len(self.tokens):
            return self.tokens[j]
        return (None, None)

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect_ident(self):
        kind, val = self.next()
        if kind != "IDENT":
            raise SQLSyntaxError(f"expected identifier, got {val}")
        return val

    def finish(self):
        kind, val = self.peek()
        if kind is not None:
            raise SQLSyntaxError(f"unexpected trailing token: {val}")


def parse(sql):
    tokens = tokenize(sql)
    p = Parser(tokens)
    kind, keyword = p.next()
    if kind != "IDENT":
        raise SQLSyntaxError("expected SQL statement")
    stmt = keyword.upper()
    if stmt == "CREATE":
        parse_create(p)
    elif stmt == "DROP":
        parse_drop(p)
    elif stmt == "SELECT":
        parse_select(p)
    elif stmt == "INSERT":
        parse_insert(p)
    elif stmt == "UPDATE":
        parse_update(p)
    elif stmt == "DELETE":
        parse_delete(p)
    else:
        raise SQLSyntaxError(f"unsupported statement: {stmt}")
    p.finish()


def parse_create(p):
    kind, val = p.next()
    if (kind, val) != ("IDENT", "table"):
        raise SQLSyntaxError("CREATE requires TABLE")
    name = p.expect_ident()
    if_present = False
    not_present = False
    if p.peek() == ("IDENT", "if"):
        p.next()
        if p.peek() == ("IDENT", "not"):
            p.next()
            not_present = True
        if p.next() != ("IDENT", "present"):
            raise SQLSyntaxError("expected PRESENT after IF")
        if_present = True
    _, paren = p.next()
    if paren != "(":
        raise SQLSyntaxError("expected ( after CREATE TABLE name")
    columns = []
    while True:
        columns.append(p.expect_ident())
        # optional column type name(s), e.g. VARCHAR(255), INT - ignored
        while True:
            k, v = p.peek()
            if k == "IDENT" or (k == "OP" and v == "("):
                p.next()
                k2, v2 = p.peek()
                if k == "OP" and v == "(" and k2 == "NUMBER":
                    p.next()
                    if p.peek()[1] == ")":
                        p.next()
                continue
            break
        _, val2 = p.peek()
        if val2 == ",":
            p.next()
            continue
        if val2 == ")":
            p.next()
            break
        raise SQLSyntaxError("expected , or ) in column list")
    return ("create", name, columns, not_present)


def parse_drop(p):
    kind, val = p.next()
    if (kind, val) != ("IDENT", "table"):
        raise SQLSyntaxError("DROP requires TABLE")
    name = p.expect_ident()
    if_present = False
    if p.peek() == ("IDENT", "if"):
        p.next()
        if p.next() != ("IDENT", "present"):
            raise SQLSyntaxError("expected PRESENT after IF")
        if_present = True
    return ("drop", name, if_present)


def parse_insert(p):
    kind, val = p.next()
    if (kind, val) != ("IDENT", "into"):
        raise SQLSyntaxError("INSERT requires INTO")
    name = p.expect_ident()
    _, paren = p.next()
    if paren != "(":
        raise SQLSyntaxError("expected ( after table name")
    columns = []
    while True:
        columns.append(p.expect_ident())
        _, val = p.peek()
        if val == ",":
            p.next()
            continue
        if val == ")":
            p.next()
            break
        raise SQLSyntaxError("expected , or ) in column list")
    kind, val = p.next()
    if (kind, val) != ("IDENT", "values"):
        raise SQLSyntaxError("INSERT requires VALUES")
    _, paren = p.next()
    if paren != "(":
        raise SQLSyntaxError("expected ( after VALUES")
    values = []
    while True:
        kind, val = p.next()
        if kind not in ("STRING", "NUMBER"):
            raise SQLSyntaxError("expected value literal")
        values.append(str(val) if kind == "NUMBER" else val)
        _, val2 = p.peek()
        if val2 == ",":
            p.next()
            continue
        if val2 == ")":
            p.next()
            break
        raise SQLSyntaxError("expected , or ) in values")
    return ("insert", name, columns, values)


def parse_select(p):
    columns = []  # list of (expr, title)
    while True:
        kind, val = p.peek()
        if kind == "OP" and val == "*":
            p.next()
            columns.append(("*", "*"))
        else:
            expr = _parse_expr(p)
            title = _expr_title(expr)
            k2, v2 = p.peek()
            if k2 == "IDENT" and v2 == "as":
                p.next()
                title = p.expect_ident()
            elif k2 == "IDENT" and v2 not in ("from", "where"):
                title = p.expect_ident()
            columns.append((expr, title))
        _, val = p.peek()
        if val == ",":
            p.next()
            continue
        break
    kind, val = p.next()
    if (kind, val) != ("IDENT", "from"):
        raise SQLSyntaxError("SELECT requires FROM")
    name = p.expect_ident()
    where = None
    kind, val = p.peek()
    if (kind, val) == ("IDENT", "where"):
        p.next()
        where = _parse_expr(p)
    return ("select", name, columns, where)


def _expr_title(expr):
    if expr[0] == "col":
        return expr[1]
    if expr[0] == "lit":
        return str(expr[1])
    if expr[0] == "cmp":
        return expr[1]
    if expr[0] == "op":
        return _expr_title(expr[2]) if _expr_title(expr[2]) else "expr"
    return "expr"


def parse_update(p):
    name = p.expect_ident()
    kind, val = p.next()
    if (kind, val) != ("IDENT", "set"):
        raise SQLSyntaxError("UPDATE requires SET")
    assignments = []
    while True:
        col = p.expect_ident()
        kind, val = p.next()
        if kind != "OP" or val != "=":
            raise SQLSyntaxError("expected = in SET")
        kind, val = p.next()
        if kind not in ("STRING", "NUMBER"):
            raise SQLSyntaxError("expected value in SET")
        assignments.append((col, str(val) if kind == "NUMBER" else val))
        _, val2 = p.peek()
        if val2 == ",":
            p.next()
            continue
        break
    where = None
    kind, val = p.peek()
    if (kind, val) == ("IDENT", "where"):
        p.next()
        where = _parse_expr(p)
    return ("update", name, assignments, where)


def parse_delete(p):
    kind, val = p.peek()
    if (kind, val) == ("IDENT", "from"):
        p.next()
    name = p.expect_ident()
    where = None
    kind, val = p.peek()
    if (kind, val) == ("IDENT", "where"):
        p.next()
        where = _parse_expr(p)
    return ("delete", name, where)


def _parse_expr(p):
    left = _parse_term(p)
    kind, val = p.peek()
    if kind == "IDENT" and val in ("and", "or"):
        p.next()
        right = _parse_term(p)
        return ("op", val, left, right)
    return left


def _parse_term(p):
    kind, val = p.next()
    if kind == "OP" and val == "(":
        inner = _parse_expr(p)
        if p.next()[1] != ")":
            raise SQLSyntaxError("expected )")
        return inner
    if kind == "IDENT":
        # could be a column, or a comparison col=value
        comp_kind, comp_val = p.peek()
        if comp_kind == "OP" and comp_val in ("=", "<>", ">", "<", ">=", "<="):
            p.next()
            rk, rv = p.next()
            if rk not in ("STRING", "NUMBER", "IDENT"):
                raise SQLSyntaxError("expected value in comparison")
            return ("cmp", val, comp_val, rv)
        return ("col", val)
    if kind in ("STRING", "NUMBER"):
        return ("lit", val)
    raise SQLSyntaxError(f"unexpected token {val} in expression")


def eval_expr(expr, row):
    kind = expr[0]
    if kind == "col":
        return row.get(expr[1])
    if kind == "lit":
        return expr[1]
    if kind == "cmp":
        col = row.get(expr[1])
        val = expr[3]
        op = expr[2]
        return compare(col, val, op)
    if kind == "op":
        left = eval_expr(expr[2], row)
        right = eval_expr(expr[3], row)
        if expr[1] == "and":
            return bool(left) and bool(right)
        return bool(left) or bool(right)
    raise ValueError(f"unknown expr {expr}")


def _eval_select(expr, row):
    if expr[0] == "col":
        return row.get(expr[1])
    if expr[0] == "lit":
        return expr[1]
    return eval_expr(expr, row)


def compare(col, val, op):
    if op == "=":
        return str(col) == str(val)
    if op == "<>":
        return str(col) != str(val)
    try:
        a, b = float(col), float(val)
    except (TypeError, ValueError):
        return False
    if op == ">":
        return a > b
    if op == "<":
        return a < b
    if op == ">=":
        return a >= b
    if op == "<=":
        return a <= b
    return False


class Executor:
    def __init__(self, db):
        self.db = db

    def execute(self, sql):
        tokens = tokenize(sql)
        p = Parser(tokens)
        kind, keyword = p.next()
        if kind != "IDENT":
            raise SQLSyntaxError("expected SQL statement")
        stmt = keyword.upper()
        if stmt == "CREATE":
            return self.do_create(parse_create(p))
        if stmt == "DROP":
            return self.do_drop(parse_drop(p))
        if stmt == "INSERT":
            return self.do_insert(parse_insert(p))
        if stmt == "SELECT":
            return self.do_select(parse_select(p))
        if stmt == "UPDATE":
            return self.do_update(parse_update(p))
        if stmt == "DELETE":
            return self.do_delete(parse_delete(p))
        raise SQLSyntaxError(f"unsupported statement: {stmt}")

    def do_create(self, parsed):
        _, name, columns, if_not_present = parsed
        if if_not_present and self.db.table_exists(name):
            return ("create", name, False)
        self.db.create_table(name, columns)
        return ("create", name, True)

    def do_drop(self, parsed):
        _, name, if_present = parsed
        if if_present and not self.db.table_exists(name):
            return ("drop", name, False)
        self.db.drop_table(name)
        return ("drop", name, True)

    def do_insert(self, parsed):
        _, name, columns, values = parsed
        tbl = self.db.get_table(name)
        if len(columns) != len(values):
            raise XlsxError("column count does not match value count")
        for c in columns:
            if c not in tbl.columns:
                raise XlsxError(f'unknown column "{c}" in table "{name}"')
        if ID_COLUMN in columns:
            raise XlsxError("cannot insert into id column")
        data = dict(zip(columns, values))
        newid = tbl.append(data)
        return ("insert", newid)

    def do_select(self, parsed):
        _, name, columns, where = parsed
        tbl = self.db.get_table(name)
        rows = tbl.read_all()
        if where:
            rows = [r for r in rows if eval_expr(where, r)]
        if len(columns) == 1 and columns[0][0] == "*":
            cols = tbl.columns
            out = [[r.get(c) for c in cols] for r in rows]
            return ("select", cols, out)
        cols = [title for _, title in columns]
        out = []
        for r in rows:
            out.append([_eval_select(expr, r) for expr, _ in columns])
        return ("select", cols, out)

    def do_update(self, parsed):
        _, name, assignments, where = parsed
        tbl = self.db.get_table(name)
        for col, _ in assignments:
            if col == ID_COLUMN:
                raise XlsxError("cannot update id column")
            if col not in tbl.columns:
                raise XlsxError(f'unknown column "{col}"')
        rows = tbl.read_all()
        changed = 0
        for r in rows:
            if where and not eval_expr(where, r):
                continue
            for col, val in assignments:
                r[col] = val
            changed += 1
        tbl.write_all(rows)
        return ("update", changed)

    def do_delete(self, parsed):
        _, name, where = parsed
        tbl = self.db.get_table(name)
        rows = tbl.read_all()
        before = len(rows)
        if where:
            rows = [r for r in rows if not eval_expr(where, r)]
        else:
            rows = []
        tbl.write_all(rows)
        return ("delete", before - len(rows))
