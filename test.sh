#!/bin/sh

echo "Running unit tests from directory /unittests"

export TESTING=true

.webscraper-venv/bin/python3 -m unittest discover ./unittests


# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#activate-a-virtual-environment
# env is now ready I can definitely run it from laptop