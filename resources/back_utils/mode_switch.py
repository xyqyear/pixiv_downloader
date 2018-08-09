# coding = utf-8

from .downloader import Download


# choose 方法选择下载模式并返回用于下载的方法对象
class ModeSwitch:

    def __init__(self, pipe, api):
        self.pipe = pipe
        self.api = api
        self.download = Download(pipe, api)
        self.modes = {"bookmarks": self.bookmarks,
                      "painter": self.painter,
                      "ranking": self.ranking}

    def choose(self, working_mode):
        return self.modes[working_mode]

    def bookmarks(self):
        user_uid = self.require("user_uid")["value"]
        self.pipe.set("开始下载收藏夹", "data")
        self.download.bookmarks(user_uid)
        print("bookmark downloader start")

    def painter(self):
        painter_uid = self.require("painter_uid")["value"]
        self.pipe.set("开始下载画师作品", "data")
        self.download.works(painter_uid)
        print("painter downloader start")

    def ranking(self):
        rank_type = self.require("rank_type")["value"]
        date = self.require("rank_date")["value"]
        self.pipe.set("开始下载排行榜", "data")
        self.download.ranking(date, rank_type)
        print("ranking downloader start")

    def test(self):
        import json
        print(json.dumps(self.api.illust_ranking(mode='day_female_r18')))

    def require(self, command):
        self.pipe.set(command, "command")
        info = self.pipe.get()
        return info
