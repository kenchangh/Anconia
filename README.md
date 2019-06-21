# Anconia

Implementation of the Avalanche consensus protocol. Avalanche is a performant, leaderless, secure consensus protocol.

## Setup & Installation

The use of virtualenv is needed to run the project. The project uses Python3.6+.

```
virtualenv -p python3.6 venv
```

Then, install the dependencies

```
pip install -r requirements.txt
```

## Running the testnet

The `src/testnet.sh` script will spawns a Redis server and local processes that will interact with each other in a peer-to-peer fashion.

These nodes will randomly generate transactions to fill up the blockchain.

```
cd src
./testnet.sh

# add MAX_NODES to increase the number of nodes in the local network
MAX_NODES=15 ./testnet.sh
```

## Running tests

From the root directory, run the command:

```
python -m pytest tests
```
