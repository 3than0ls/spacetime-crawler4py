#!/bin/sh

echo "Running unit tests from ./test.sh..."

for file in unittests/test_*.py; do
    echo "-------------------------------------------------------------------------"
    echo "==== Running unit tests found in $file ===="
    echo "-------------------------------------------------------------------------"
    python -m unittest $file
done
