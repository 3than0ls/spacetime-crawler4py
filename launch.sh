#!/bin/sh


echo "My 3 tries for running during the deployment period have passed."
exit 1


ARGS=""
if [ "$1" = "--restart" ]; then
  ARGS="--restart"
fi

.webscraper-venv/bin/python3 launch.py $ARGS
