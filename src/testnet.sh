#!/usr/bin/env bash

max=5
port=5000

function cleanup {
  kill $(jobs -p)
}

for i in `seq 0 $max`
do
  printf "Running node $i\n"
  python3 main.py --host 127.0.0.1 --port $port &
  sleep 3
  ((port++))
done

trap cleanup EXIT
