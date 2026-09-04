#!/usr/bin/env bash

echo "Running Zig connect tests ..."
echo

cd test/zig
zig build run
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Zig tests PASSED."
else
    echo "Zig tests FAILED."
fi

exit "$FAILED"
