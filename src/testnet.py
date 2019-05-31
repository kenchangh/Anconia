from multiprocessing import Process
from main import Anconia
import os
import sys


def start_anconia(host, port):
    anconia = Anconia()
    anconia.start(host=host, port=port)


def launch_testnet(network_size=10):
    processes = []
    try:
        addr = '127.0.0.1'
        start_port = 5000
        for i in range(network_size):
            port = start_port + i
            p = Process(target=start_anconia, args=(addr, port))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
    except:
        for p in processes:
            p.terminate()


if __name__ == '__main__':
    launch_testnet()
