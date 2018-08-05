# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.operations import login, work

if __name__ == '__main__':
    aapi = AppPixivAPI()
    login(aapi)
    work(aapi)