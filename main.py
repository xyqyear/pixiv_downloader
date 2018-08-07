# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.managers import UserManager
from resources.mode import ModeSwitcher



if __name__ == '__main__':
    aapi = AppPixivAPI()
    user_manager = UserManager()
    mode_switcher = ModeSwitcher(aapi)

    user_manager.login(aapi)
    mode_switcher.start()
