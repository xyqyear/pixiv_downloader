# coding = utf-8

from .downloader import Download


# choose 方法选择下载模式并返回用于下载的方法对象
class ModeSwitch:

    def __init__(self, pipe):
        self.pipe = pipe
        self.modes = {"bookmarks": self.bookmarks,
                      "painter": self.painter,
                      "ranking": self.ranking}

    def choose(self, working_mode):
        return self.modes[working_mode]

    def bookmarks(self):
        # 正式版此处应为通过self.pipe 向前端报告工作进度
        # print 仅为测试用
        self.pipe.set("开始下载收藏夹", "data")
        print("bookmark downloader start")

    def painter(self):
        # 正式版此处应为通过self.pipe 向前端报告工作进度
        # print 仅为测试用
        self.pipe.set("开始下载画师作品", "data")
        print("painter downloader start")

    def ranking(self):
        # 正式版此处应为通过self.pipe 向前端报告工作进度
        # print 仅为测试用
        self.pipe.set("开始下载排行榜", "data")
        print("ranking downloader start")

    def test(self):

    def require(self, command):
        self.pipe.set(command, "command")
        info = self.pipe.get()
        return info
