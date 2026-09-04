#!/usr/bin/env bash

if [ -z "$PYTHON" ]; then
    if command -v python3 >/dev/null 2>&1; then PYTHON=python3
    elif command -v python >/dev/null 2>&1; then PYTHON=python
    else echo "Error: python not found" >&2; exit 1
    fi
fi

echo "Running Python connect tests ..."
echo

cd test/python
"$PYTHON" test_connect.py
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Python tests PASSED."
else
    echo "Python tests FAILED."
fi

exit "$FAILED"
