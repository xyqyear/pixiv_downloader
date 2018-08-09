# coding = utf-8

from multiprocessing.dummy import Process
from .back_utils import handshaker, mode_switch

login = handshaker.Handshaker()


class BackEnd(Process):

    # 从主程序中获取通讯端口，进程锁，以及得知父进程
    def __init__(self, communicator, t_lock, parent):
        # 线程初始化
        Process.__init__(self)
        self.switch = mode_switch.ModeSwitch(communicator)
        self.communicator = communicator
        self.lock = t_lock
        self._parent = parent

    def run(self):
        self.lock_print("Backend.run()")
        self.lock_print("Backend acquire login info")
        # 向前端要求登录信息. 应增加判断是否存在token 的功能
        login_info = self.acquire("get_login_info")["value"]
        self.lock_print(f"Backend got login_info: {login_info}")
        self.lock_print("Backend login start")
        # login 方法回传登录是否成功
        login_success = login.start(*login_info)
        self.lock_print(f"Backend login_success: {login_success}")
        while True:
            # 询问前端工作模式并进行下载
            self.lock_print("Backend acquire working mode")
            working_mode = self.acquire("get_working_mode")["value"]
            self.lock_print(f"Backend got working_mode: {working_mode}")
            downloader = self.switch.choose(working_mode)
            downloader()
            self.lock_print("---- Backend download finish ----")

    # 向前端要求数据的方法. 此实现有风险，若前端因某些原因无回传数据会死锁
    # 后续尝试改进
    def acquire(self, command):
        self.communicator.set(command, "command")
        info = self.communicator.get()
        return info

    # 用于测试时的带锁print
    def lock_print(self, text):
        self.lock.acquire()
        print(text)
        self.lock.release()


if __name__ == "__main__":
    thread1 = BackEnd(None, None)
    thread1.start()
