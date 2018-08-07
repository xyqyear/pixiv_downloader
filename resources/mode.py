# -*- coding:utf-8 -*-
import re

from .downloader import Download
from .utils import get_yesterday_date


class ModeSwitcher:

    def __init__(self, api_object):
        self.modes = {"1": self.mode1,
                      "2": self.mode2,
                      "3": self.mode3,
                      "4": self.mode4}
        self.api_object = api_object
        self.download = Download()

    def start(self):
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

        self.download.works(self.api_object, uid)

    def mode2(self):
        while True:
            uid = input('请输入用户uid:')
            if uid.isdigit():
                break
            else:
                print('请输入正确的用户uid!')

        self.download.bookmarks(self.api_object, uid)

    def mode3(self):
        while True:
            raw_date = input('请输入下载日期，格式为 yyyy-mm-dd  分隔符可用. / - : | 或空格\n如果需要下载昨天的，请直接回车:')
            if raw_date == '':
                date = get_yesterday_date()
                break
            found_date = re.findall(r"(\d{4})[./\-:|](\d{1,2})[./\-:|](\d{1,2})", raw_date)[0]
            if found_date:
                date = f"{0}-{1}-{2}"(found_date)
                break
            print('请输入正确的日期格式\n')

        modes = {'0': 'day', '1': 'day_original', '2': 'day_rookie',
                 '3': 'week', '4': 'week_original', '5': 'week_rookie',
                 '6': 'month', '7': 'month_original', '8': 'month_rookie',
                 '9': 'day_male', '10': 'day_female',
                 '11': 'day_manga', '12': 'week_manga', '13': 'month_manga',

                 '14': 'day_r18', '15': 'week_r18', '16': 'month_r18',
                 '17': 'day_male_r18', '18': 'day_female_r18',
                 '19': 'day_r18_manga', '20': 'week_r18_manga', '21': 'month_r18_manga'}
        while True:
            mode_digit = input('''
请输入下载什么榜单，对应表如下:
        0：日榜       1：日榜，首次上榜  2：日榜，曾上过榜
        3：周榜       4：周榜，首次上榜  5：周榜，曾上过榜
        6：月榜       7：月榜，首次上榜  8：月榜，曾上过榜
        9：日榜，男性向                 10：日榜，女性向
        11：日榜漫画  12：周榜漫画       13：月榜漫画

        14：日榜r18     15：周榜r18     16：月榜r18
        17：日榜男性向r18               18：日榜女性向r18
        19：日榜r18漫画 20：周榜r18漫画 21：月榜r18漫画
请输入一个数字:''')
            if mode_digit in modes:
                mode = modes[mode_digit]
                break
            else:
                print('请输入正确的模式')

        self.download.ranking(self.api_object, date, mode)

    def mode4(self):
        import json
        print(json.dumps(self.api_object.illust_ranking()))
