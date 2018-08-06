# -*- coding:utf-8 -*-
from .features import download_works, download_bookmarks

def work(api_object):
    """
    确定工作模式并工作
    :return: 
    """
    while True:
        mode = input('请输入工作模式(1是下载画师作品,2是下载收藏夹,3是下载排行榜):')
        if mode in ['1', '2', '3', '4']:
            break
        print('请重新输入!')

    if mode == '1':
        while True:
            uid = input('请输入画师uid:')
            if uid.isdigit():
                break
            print('请输入正确的画师uid!')

        download_works(api_object, uid)

    if mode == '2':
        while True:
            uid = input('请输入用户uid:')
            if uid.isdigit():
                break
            print('请输入正确的用户uid!')

        download_bookmarks(api_object, uid)

    if mode == '3':
        pass

    # Test Mode
    if mode == '4':
        print(api_object.user_detail('13665349'))