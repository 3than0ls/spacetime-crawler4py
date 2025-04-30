#!/bin/sh

ARGS=""
if [ "$1" = "--restart" ]; then
  ARGS="--restart"
fi

.webscraper-venv/bin/python3 launch.py $ARGS
