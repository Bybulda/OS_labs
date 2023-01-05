import multiprocessing
import socket
from multiprocessing import Queue
from threading import Thread
from json import loads
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


HOST = "127.0.0.1"
PORT_1 = 65430
PORT_2 = 65429


class Server:
    def __init__(self, queue: multiprocessing.Queue, host: str):
        self.q, self.host = queue, host

    def listner(self, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = ' '
                while data != b'':
                    data = conn.recv(1024)
                    if data == b'':
                        break
                    self.q.put(data)

    def client_server(self, port1: int, port2: int):
        client1 = Thread(target=self.listner, args=(port1,))
        client2 = Thread(target=self.listner, args=(port2,))
        client1.start()
        client2.start()
        client1.join()
        client2.join()
        self.serialize_data()

    def serialize_data(self):
        data = ''
        while not self.q.empty():
            data = f'{data}{self.q.get().decode("utf-8")}'
        print(*data.split('###')[:-1], sep='\n')


if __name__ == '__main__':
    queue = Queue()
    serv = Server(queue, host=HOST)
    serv.client_server(PORT_1, PORT_2)
