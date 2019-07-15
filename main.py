# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.managers import UserManager, ProxyManager
from resources.mode import ModeSwitcher


if __name__ == '__main__':
    proxies = ProxyManager().proxies
    aapi = AppPixivAPI(proxies=proxies)
    user_manager = UserManager(aapi)
    mode_switcher = ModeSwitcher(aapi, proxies)

    user_manager.login()
    mode_switcher.start()
