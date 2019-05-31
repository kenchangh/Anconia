#!/usr/bin/env bash

max=4
port=5000

function cleanup {
  kill $(jobs -p)
}

trap cleanup EXIT

for i in `seq 0 $max`
do
  printf "Running node $i\n"
  python3 main.py --verbose --host 127.0.0.1 --port $port &
  sleep 3
  ((port++))
done

while true; do sleep 86400; done
