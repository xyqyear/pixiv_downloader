# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.login import login
from resources.mode import work

if __name__ == '__main__':
    aapi = AppPixivAPI()
    login(aapi)
    work(aapi)
