# coding = utf-8

from multiprocessing.dummy import Process
from .back_utils import handshaker, mode_switch
from .protocol import commands

login = handshaker.Handshaker()
switch = mode_switch.ModeSwitch()


class BackEnd(Process):

    def __init__(self, communicator, t_lock):
        self.communicator = communicator
        self.lock = t_lock

    def run(self):
        self.lock_print("Backend.run()")
        self.lock_print("Backend acquire login info")
        login_info = self.acquire("login_info")
        self.lock_print(f"Backend got login_info: {login_info}")
        self.lock_print("Backend login start")
        login.start(*login_info)
        working_mode = self.acquire("working_mode")
        downloader = switch.choose(working_mode)
        downloader.start()

    def acquire(self, command):
        self.communicator.send(commands[command])
        pack = self.communicator.recv()
        info = pack.info
        return info

    # 用于测试时的带锁print
    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()


if __name__ == "__main__":

    thread1 = BackEnd(None, None)
    thread1.start()
