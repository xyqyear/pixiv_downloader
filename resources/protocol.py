# -*- encoding:utf-8 -*-

from multiprocessing import Pipe
import sys


class ProtocolPipe:

    def __init__(self):
        (self._p0, self._p1) = Pipe()
        self._c0 = Wrap(self._p0)
        self._c1 = Wrap(self._p1)

    def __call__(self):
        return self._c0, self._c1


class Wrap:

    def __init__(self, connection):
        self.connection = connection
        self.recv = self.connection.recv

    def send(self, info, info_type="data"):
        sender = sys._getframe(1).f_code.co_name
        pack = Pack(info, info_type, sender)
        self.connection.send(pack)


class Pack:

    def __init__(self, info, info_type, sender):
        self.info = info
        self.info_type = info_type
        self.sender = sender
