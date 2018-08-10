# coding = utf-8

from multiprocessing.dummy import Process
from .back_utils import handshaker, mode_switch
from pixivpy3 import AppPixivAPI


class BackEnd(Process):

    # 从主程序中获取通讯端口，进程锁，以及得知父进程
    def __init__(self, pipe, t_lock, parent):
        # 线程初始化
        Process.__init__(self)
        self.__name__ = "BackEnd"
        self.api = AppPixivAPI()
        self.pipe = pipe
        self.login = handshaker.HandShaker(pipe, self.api)
        self.switch = mode_switch.ModeSwitch(pipe, self.api)
        self.lock = t_lock
        self._parent = parent

    # 这里pipe.set 和pipe.report 方法看起来差不多，
    # pipe.report 是前端必要知道的状态信息
    # pipe.set 则是让前端显示了临时用于调试的信息
    def run(self):
        self.pipe.debug("BackEnd start", self.__name__)
        # login 方法回传登录是否成功
        self.login.start()
        while True:
            # 询问前端工作模式并进行下载
            working_mode = self.pipe.require("working_mode", sender=self.__name__)["value"]
            self.pipe.debug(f"Backend got working_mode: {working_mode}", self.__name__)
            downloader = self.switch.choose(working_mode)
            downloader()
            self.pipe.debug("download finish", self.__name__)

