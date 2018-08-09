# coding = utf-8

from multiprocessing.dummy import Process
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
        self.mapping = {"get_working_mode": self.send_working_mode,
                        "get_username": self.get_username,
                        "get_password": self.get_password,
                        "token_strategy": self.get_token_strategy}

    def run(self):
        self.lock_print("Frontend.run()")
        while True:
            self.lock_print("Frontend waiting information")
            # 等待后端传来指令
            info = self.wait_for_info()
            self.lock_print(f"Frontend got info: {info}")
            if info["value_type"] == "command":
                self.mapping[info["value"]]()
            else:
                self.lock_print(info["value"])

    def get_username(self):
        self.lock_print("请输入用户名(或邮箱地址):")
        username = input()
        self.communicator.set(username, "data")
        self.lock_print("Frontend sent username")

    def get_password(self):
        self.lock_print("请输入密码:")
        password = input()  ######## 为方便测试这里使用的是input！！！！
                            ######## 调试完成后务必！！改回getpass.getpass ！！！！
        self.communicator.set(password, "data")
        self.lock_print("Frontend sent password")

    def get_token_strategy(self):
        self.lock_print("是否保留服务器返回的通行证以便下次登录？")
        self.lock_print("0: 不保存 1: 保存  （默认保留通行证）")
        token_strategy = input()
        if token_strategy == "0":
            save_token = False
        else:
            save_token = True
        self.communicator.set(save_token, "data")
        self.lock_print("Frontend sent token_strategy")

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
                self.communicator.set(working_mode, "data")
                self.lock_print("Frontend sent working mode")
                break
            else:
                self.lock_print("不可识别的指令")

    # 应增加功能：判断内容类型，分别处理
    def wait_for_info(self):
        info = self.communicator.get()
        return info

    def lock_print(self, text):
        self.lock.require()
        print(text)
        self.lock.release()
