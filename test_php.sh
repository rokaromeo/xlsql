#!/usr/bin/env bash

echo "Running PHP connect tests ..."
echo

php test/php/test_connect.php
FAILED=$?

echo
if [ "$FAILED" -eq 0 ]; then
    echo "PHP tests PASSED."
else
    echo "PHP tests FAILED."
fi

exit "$FAILED"
