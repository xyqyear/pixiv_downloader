# coding = utf-8

from multiprocessing.dummy import Process
from .protocol import Pack
import getpass


class FrontEnd(Process):

    def __init__(self, communicator, t_lock, parent):
        Process.__init__(self)
        self.communicator = communicator
        self.lock = t_lock
        self._parent = parent
        self.mapping = {"get_login_info": self.send_login_info,
                        "get_working_mode": self.send_working_mode}

    def run(self):
        self.lock_print("Frontend.run()")
        while True:
            self.lock_print("Frontend waiting command")
            command = self.wait_for_command()
            self.lock_print(f"Frontend got command: {command}")
            self.mapping[command]()

    def send_login_info(self):
        print('请输入用户名(或邮箱地址)和密码来登录')
        username = input('请输入用户名(或邮箱地址): ')
        password = input('请输入密码: ') ######## 为方便测试这里使用的是input！！！！
                                        ######## 调试完成后务必！！改回getpass.getpass ！！！！
        login_info = (username, password)
        self.communicator.send(Pack(login_info))
        self.lock_print("Frontend sent login info")

    def send_working_mode(self):
        command_mapping = {"1": "painter",
                           "2": "bookmarks",
                           "3": "ranking"}
        print("选择工作模式：")
        print("1: 下载画师作品  2: 下载收藏夹  3: 下载排行榜")
        while True:
            command = input()
            if command in command_mapping:
                working_mode = command_mapping[command]
                self.communicator.send(Pack(working_mode))
                self.lock_print("Frontend sent working mode")
                break
            else:
                self.lock_print("不可识别的指令")

    def wait_for_command(self):
        pack = self.communicator.recv()
        return pack.info

    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()
