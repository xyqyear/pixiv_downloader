# coding = utf-8

from threading import Thread
from .back_utils import handshaker, mode_switch
from .protocol import commands

login = handshaker.Handshaker()


class BackEnd(Thread):

    def __init__(self, communicator):
        Thread.__init__(self)
        self.communicator = communicator

    def run(self):
        login_info = self.get_login_info()
        login.start(login_info)
        working_mode = self.get_working_mode()
        downloader = mode_switch(working_mode)
        downloader.start()

    def get_login_info(self):
        self.communicator.append(commands["get_login_info"])
        while self.communicator.empty():
            pass
        pack = self.communicator.get()
        login_info = pack.




if __name__ == "__main__":

    thread1 = BackEnd()
    thread1.start()
