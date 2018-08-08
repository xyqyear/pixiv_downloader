# coding = utf-8


class ModeSwitch:

    def __init__(self):
        self.modes = {"bookmarks": self.bookmarks,
                      "painter": self.painter,
                      "ranking": self.ranking}

    def choose(self, working_mode):
        return self.modes[working_mode]

    def bookmarks(self):
        pass

    def painter(self):
        pass

    def ranking(self):
        pass
