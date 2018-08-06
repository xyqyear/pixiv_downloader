# -*- coding:utf-8 -*-
from .features import download_works, download_bookmarks

class mode_switch():

    def __init__(self):
        self.modes = {"1":self.mode1,
                      "2":self.mode2,
                      "3":self.mode3,
                      "4":self.mode4}
    
    def start(api_object):
        """
        确定工作模式并工作
        :return: 
        """

        while True:
            mode = input('请输入工作模式(1是下载画师作品,2是下载收藏夹,3是下载排行榜):')
            if mode in self.modes:
                self.modes[mode]()
            else:
                print('请重新输入!')

    def mode1(self):
        while True:
            uid = input('请输入画师uid:')
            if uid.isdigit():
                break
            else:
                print('请输入正确的画师uid!')

        download_works(api_object, uid)

    def mode2(self):
        while True:
            uid = input('请输入用户uid:')
            if uid.isdigit():
                break
            else:
                print('请输入正确的用户uid!')

        download_bookmarks(api_object, uid)

    def mode3(self):
        pass

    def mode4(self):
        print(api_object.user_detail('13665349'))
        

