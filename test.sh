#!/bin/sh

echo "Running unit tests from directory /unittests"

export TESTING=true

.webscraper-venv/bin/python3 -m unittest discover ./unittests
