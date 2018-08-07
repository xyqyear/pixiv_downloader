# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.login import UserManager
from resources.mode import ModeSwitcher

user_manager = UserManager()

if __name__ == '__main__':
    aapi = AppPixivAPI()

    user_manager.login(aapi)
    new_mode_switcher = ModeSwitcher(aapi)
    new_mode_switcher.start()
