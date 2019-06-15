#!/usr/bin/env bash

if [[ -z "${MAX_NODES}" ]]; then
  max=8
else
  max=$MAX_NODES
fi

port=5000

function cleanup {
  kill $(jobs -p)
}

trap cleanup EXIT

# python3 main.py --analytics True --host 127.0.0.1 --port $port &
python3 main.py --host 127.0.0.1 --port $port &
sleep 3
((port++))

for i in `seq 1 $max`
do
  printf "Running node $i\n"
  python3 main.py --host 127.0.0.1 --port $port &
  sleep 3
  ((port++))
done

while true; do sleep 86400; done
