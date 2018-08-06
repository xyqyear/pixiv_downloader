# -*- coding:utf-8 -*-

from pixivpy3 import AppPixivAPI
from resources.login import user_manager
from resources.mode import mode_switch

if __name__ == '__main__':
    token_holder = user_manager()
    
    aapi = AppPixivAPI()
    token_holder.login(aapi)
    mode_switch.start(aapi)
