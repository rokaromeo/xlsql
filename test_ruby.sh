#!/usr/bin/env bash

echo "Running Ruby connect tests ..."
echo

cd test/ruby
ruby -S bundle exec ruby connect_test.rb
FAILED=$?
cd ../..

echo
if [ "$FAILED" -eq 0 ]; then
    echo "Ruby tests PASSED."
else
    echo "Ruby tests FAILED."
fi

exit "$FAILED"
