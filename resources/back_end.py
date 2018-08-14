# -*- encoding:utf-8 -*-

from multiprocessing.dummy import Process
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
        login_success = False
        while not login_success:
            if tokens:
                self.pipe.send(["tokens", tokens])
                self.pipe.send("login_strategy", "require")
                login_strategy = self.pipe.recv().info
                if login_strategy == "token":
                    login_success = self.login.login_with_token()
                elif login_strategy == "password":
                    self.pipe.send("username", "require")
                    username = self.pipe.recv().info
                    self.pipe.send("password", "require")
                    password = self.pipe.recv().info
                    login_success = self.login.login_with_password(username, password)
            else:
                self.pipe.send("username", "require")
                username = self.pipe.recv().info
                print(f"Back get username {username}")
                self.pipe.send("password", "require")
                password = self.pipe.recv().info
                print(f"Back get password {password}")
                login_success = self.login.login_with_password(username, password)
        self.pipe.send("token_strategy", "require")
        token_strategy = self.pipe.recv().info
        self.login.save_token(token_strategy)
        while True:
            self.pipe.send("working_mode", "require")
            working_mode = self.pipe.recv().info
            (download, download_info) = self.prepare_working(working_mode)
            for info in download(*download_info):
                self.pipe.send(info, "state")

    def prepare_working(self, working_mode):
        if working_mode == "ranking":
            self.pipe.send("rank_type", "require")
            rank_type = self.pipe.recv().info
            self.pipe.send("rank_date", "require")
            rank_date = self.pipe.recv().info
            return (self.downloader.ranking, (rank_date, rank_type))
        elif working_mode == "bookmarks":
            self.pipe.send("user_uid", "require")
            user_uid = self.pipe.recv().info
            return (self.downloader.bookmarks, (user_uid))
        elif working_mode == "painter":
            self.pipe.send("painter_uid", "require")
            painter_uid = self.pipe.recv().info
            return (self.downloader.painter, (painter_uid))

