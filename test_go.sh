#!/usr/bin/env bash

echo "Running Go connect tests ..."
echo

cd test/go
go run .
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Go tests PASSED."
else
    echo "Go tests FAILED."
fi

exit "$FAILED"
