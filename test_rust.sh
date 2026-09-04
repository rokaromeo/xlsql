#!/usr/bin/env bash

echo "Running Rust connect tests ..."
echo

cd test/rust
cargo run --quiet
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Rust tests PASSED."
else
    echo "Rust tests FAILED."
fi

exit "$FAILED"
