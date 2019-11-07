#!/usr/bin/env python3


class SocketBase:
    def __init__(self, header_size, encoding):
        self.__header_size = header_size
        self.__encoding = encoding

    def receive_message(self, socket_):
        new_msg = True
        msg = ''
        while True:
            msg_part = socket_.recv(16)
            if new_msg:
                msg_len = int(msg_part[:self.get_header_size()])
                new_msg = False
            msg += msg_part.decode(self.get_encoding())

            if len(msg) - self.get_header_size() == msg_len:
                return msg

    def send_message(self, socket_, message):
        socket_.send(bytes(str(len(message)) + ' ' * (self.get_header_size() - len(str(len(message)))) + message,
                           self.get_encoding()))

    def get_header_size(self):
        return self.__header_size

    def get_encoding(self):
        return self.__encoding