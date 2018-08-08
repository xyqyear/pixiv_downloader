# coding = utf-8

from multiprocessing.dummy import Process
from .protocol import Pack  # 应在通讯管道优化之后去除加载pack， 直接使用protocol_pipe 通讯
import getpass


class FrontEnd(Process):

    # 从主程序中获取通讯端口，进程锁，以及得知父进程
    def __init__(self, communicator, t_lock, parent):
        # 线程初始化
        Process.__init__(self)
        self.communicator = communicator
        self.lock = t_lock
        self._parent = parent
        # 接收到的后端指令与要做的操作对应表
        self.mapping = {"get_login_info": self.send_login_info,
                        "get_working_mode": self.send_working_mode}

    def run(self):
        self.lock_print("Frontend.run()")
        while True:
            self.lock_print("Frontend waiting command")
            # 等待后端传来指令
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
                # 通过pipe 将工作模式告知后端
                self.communicator.send(Pack(working_mode))
                self.lock_print("Frontend sent working mode")
                break
            else:
                self.lock_print("不可识别的指令")

    # 应增加功能：判断内容类型，分别处理
    def wait_for_command(self):
        pack = self.communicator.recv()
        return pack.info

    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()
