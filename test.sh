#!/bin/sh

echo "Running unit tests from directory /unittests"

export TESTING=true

python -m unittest discover ./unittests
