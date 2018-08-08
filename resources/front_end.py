# coding = utf-8

from threading import Thread
from .protocol import Pack
import getpass


class FrontEnd(Thread):

    def __init__(self, communicator, t_lock, t_event):
        Thread.__init__(self)
        self.communicator = communicator
        self.lock = t_lock
        self.event = t_event
        self.mapping = {"get_login_info": self.send_login_info,
                        "get_working_mode": self.send_working_mode}

    def run(self):
        self.lock_print("Frontend.run()")
        while True:
            self.lock_print("Frontend wait command")
            command = self.wait_for_command()
            self.lock_print(f"Frontend got command: {command}")
            self.mapping[command]()

    def send_login_info(self):
        print('请输入用户名(或邮箱地址)和密码来登录')
        username = input('请输入用户名(或邮箱地址): ')
        password = getpass.getpass('请输入密码: ')
        login_info = (username, password)
        self.communicator.put(Pack(login_info))
        self.lock_print("Frontend sent login info")
        self.event.clear()

    def send_working_mode(self):
        print("选择工作模式：")
        print("1: 下载画师作品  2: 下载收藏夹  3: 下载排行榜")
        working_mode = input()
        self.communicator.put(Pack(working_mode))
        self.event.clear()

    def wait_for_command(self):
        while self.communicator.empty():
            pass
        pack = self.communicator.get()
        self.event.clear()
        return pack.info

    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()
