# coding = utf-8

from threading import Thread
from .back_utils import handshaker, mode_switch
from .protocol import commands

login = handshaker.Handshaker()
switch = mode_switch.ModeSwitch()


class BackEnd(Thread):

    def __init__(self, communicator, t_lock, t_event):
        Thread.__init__(self)
        self.communicator = communicator
        self.lock = t_lock
        self.event = t_event

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
        self.communicator.put(commands[command])
        self.event.clear()
        self.event.wait()
        pack = self.communicator.get()
        info = pack.info
        return info

    # 用于测试时的带锁print
    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()


if __name__ == "__main__":

    thread1 = BackEnd()
    thread1.start()
