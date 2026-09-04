#!/usr/bin/env bash

echo "Running Node.js connect tests ..."
echo

cd test/nodejs
if [ ! -d node_modules ]; then
    npm install > /dev/null
fi
npm test
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Node.js tests PASSED."
else
    echo "Node.js tests FAILED."
fi

exit "$FAILED"
