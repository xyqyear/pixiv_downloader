# coding = utf-8

from .downloader import Download


# choose 方法选择下载模式并返回用于下载的方法对象
class ModeSwitch:

    def __init__(self, pipe, api):
        self.__name__ = "ModeSwitch"
        self.pipe = pipe
        self.api = api
        self.download = Download(pipe, api)
        self.modes = {"bookmarks": self.bookmarks,
                      "painter": self.painter,
                      "ranking": self.ranking}

    def choose(self, working_mode):
        return self.modes[working_mode]

    def bookmarks(self):
        user_uid = self.pipe.require("user_uid", self.__name__)["value"]
        self.pipe.debug(f"got user_uid: {user_uid}", self.__name__)
        self.pipe.report("Downloader", "bookmarks", self.__name__)
        self.download.bookmarks(user_uid)

    def painter(self):
        painter_uid = self.pipe.require("painter_uid", self.__name__)["value"]
        self.pipe.debug(f"got painter_uid: {painter_uid}", self.__name__)
        self.pipe.report("Downloader", "painter", self.__name__)
        self.download.works(painter_uid)

    def ranking(self):
        rank_type = self.pipe.require("rank_type", self.__name__)["value"]
        self.pipe.debug(f"got rank_type: {rank_type}", self.__name__)
        date = self.pipe.require("rank_date", self.__name__)["value"]
        self.pipe.debug(f"got date: {date}", self.__name__)
        self.pipe.report("Downloader", "ranking", self.__name__)
        self.download.ranking(date, rank_type)

    def test(self):
        import json
        print(json.dumps(self.api.illust_ranking(mode='day_female_r18')))
