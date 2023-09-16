import socket
from threading import Thread
import numpy as np
from time import sleep


class SocketManager:
    def __init__(self, ip, send_port, get_port):
        self.ip = ip
        self.send_port = send_port
        self.get_port = get_port
        self.data_got = False
        self.data_reseive = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, get_port))
        self.process = Thread(target=self.read_thread, daemon=True)
        self.process.start()
        self.save_id = set()
        self.death = list()

    def send_action(self, data: (int, np.array)):
        def transform(data):
            return f"{data[0]} {np.argmax(data[1])}"

        self.socket.sendto(bytes(transform(data), 'utf-8'), (self.ip, self.send_port))

    def get_data(self):
        def transform(data: str):
            return np.asarray(list(float(i) for i in data.replace(",", ".").split(" ")))

        try:
            data, ch = self.socket.recvfrom(1024)
            data = data.decode('utf-8')
            data = transform(data)
            if self.check_entry(data) or self.check_death(data):
                return None
            return data[1:]
        except Exception as e:
            print(e)
            pass

    def check_death(self, data):
        if len(data) == 8:
            if data[7] == 1:
                if data[7] not in self.death:
                    self.death.append(data[7])
                return True
        return False

    def check_entry(self, data):
        prev_count = len(self.save_id)
        self.save_id.add(data[0])
        if prev_count == len(self.save_id):
            return True
        return False

    def read_thread(self):
        self.data_got = False
        while True:
            sleep(0.5)
            data = self.get_data()
            self.data_reseive = data
            self.data_got = True

    def read_get_data(self):
        data = None
        if self.data_got:
            self.data_got = False
            data = self.data_reseive
            self.data_reseive = None
        return data