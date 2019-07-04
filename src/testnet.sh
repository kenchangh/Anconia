#!/usr/bin/env bash

if [[ -z "${MAX_NODES}" ]]; then
  max=8
else
  max=$MAX_NODES
fi

port=5000

function cleanup {
  kill -9 $(jobs -p)
}

trap cleanup EXIT

# python3 main.py --analytics True --host 127.0.0.1 --port $port &
# python3 main.py --host 127.0.0.1 --port $port > "$port.log" 2>&1 &
# sleep 1
# ((port++))

redis-server &

redis-cli flushall

for i in `seq 1 $max`
do
  printf "Running node $i\n"
  rm -f "$port.log"
  #python3 main.py --adversarial True --host 127.0.0.1 --port $port > "$port.log" 2>&1 &
  #python3 main.py --host 127.0.0.1 --port $port > "$port.log" 2>&1 &
  python3 main.py --no-randomtx --host 127.0.0.1 --port $port &
  #python3 main.py --host 127.0.0.1 --port $port &
  sleep 1
  ((port++))
done

while true; do sleep 86400; done
