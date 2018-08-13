# -*- encoding:utf-8 -*-

from multiprocessing import Process
from pixivpy3 import AppPixivAPI
from .back_utils import handshaker, downloader


class BackEnd(Process):

    def __init__(self, pipe, parent):
        super(BackEnd, self).__init__()
        self.daemon = True
        self.pipe = pipe
        self._parent = parent

        self.api = AppPixivAPI()
        self.login = handshaker.Handshaker(self.api)
        self.downloader = downloader.Downloader(self.api)

    def run(self):
        tokens = self.login.exist_token()
        self.pipe.send(["tokens", tokens])
        login_success = False
        while not login_success:
            print(login_success)
            if tokens:
                self.pipe.send("tokens")
                self.pipe.send("login_strategy", "require")
                login_strategy = self.pipe.recv()
                if login_strategy == "token":
                    login_success = self.login.login_with_token()
                elif login_strategy == "password":
                    self.pipe.send("username", "require")
                    self.username = self.pipe.recv()
                    self.pipe.send("password", "require")
                    self.password = self.pipe.recv()
                    login_success = self.login.login_with_password(self.username, self.password)
            else:
                self.pipe.send("username", "require")
                self.username = self.pipe.recv()
                self.pipe.send("password", "require")
                self.password = self.pipe.recv()
                login_success = self.login.login_with_password(self.username, self.password)
        while True:
            self.pipe.send("working_mode", "require")
            working_mode = self.pipe.recv()
            (download, download_info) = self.prepare_working(working_mode)
            download(*download_info)

    def prepare_working(self, working_mode):
        if working_mode == "ranking":
            self.pipe.send("rank_type", "require")
            rank_type = self.pipe.recv()
            self.pipe.send("rank_date", "require")
            rank_date = self.pipe.recv()
            return self.downloader.ranking, (rank_type, rank_date)
        elif working_mode == "bookmarks":
            self.pipe.send("user_uid", "require")
            user_uid = self.pipe.recv()
            return self.downloader.bookmarks, (user_uid)
        elif working_mode == "painter":
            self.pipe.send("painter_uid", "require")
            painter_uid = self.pipe.recv()
            return self.downloader.painter, (painter_uid)
