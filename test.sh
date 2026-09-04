#!/usr/bin/env bash

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "Error: python not found" >&2
    exit 1
fi
export PYTHON

HOST="127.0.0.1"
PORT="5432"
DATA="build/python/data.xlsx"

echo "========================================"
echo " xlsql test runner"
echo "========================================"
echo

echo "[1/3] Delete build/*"
rm -rf build
mkdir -p build

echo "[2/3] Starting xlsql server on ${HOST}:${PORT} ..."
nohup "$PYTHON" server.py --host "$HOST" --port "$PORT" --data "$DATA" \
    > build/server.log 2> build/server.log.err &
SRVPID=$!

echo "Server process PID: ${SRVPID}"
echo "Waiting for server to accept connections ..."

READY=
for i in $(seq 1 30); do
    if "$PYTHON" -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('${HOST}',${PORT})); s.close()" 2>/dev/null; then
        READY=1
        break
    fi
    sleep 1
done

if [ -z "$READY" ]; then
    echo "Server did not start in time. Aborting."
    cat build/server.log
    cat build/server.log.err
    if [ -n "$SRVPID" ]; then
        echo "Stopping xlsql server process ${SRVPID} ..."
        kill "$SRVPID" 2>/dev/null || true
    fi
    exit 1
fi

echo "Server is up."
echo
echo "[3/3] Running client connect tests ..."
echo

FAILED=0

echo "--- Python ---"
bash test_python.sh || FAILED=1
echo

echo "--- Node.js ---"
bash test_nodejs.sh || FAILED=1
echo

echo "--- PHP ---"
bash test_php.sh || FAILED=1
echo

echo "--- Ruby ---"
bash test_ruby.sh || FAILED=1
echo

echo "--- Go ---"
bash test_go.sh || FAILED=1
echo

echo "--- Rust ---"
bash test_rust.sh || FAILED=1
echo

echo
echo "========================================"
if [ "$FAILED" -eq 0 ]; then
    echo "All tests PASSED."
else
    echo "Some tests FAILED."
fi
echo "========================================"

echo
echo "Stopping xlsql server ${SRVPID} ..."
kill "$SRVPID" 2>/dev/null || true
echo "Done."

exit "$FAILED"
