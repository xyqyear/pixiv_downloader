# -*- coding:utf-8 -*-
import getpass
import os

from .utils import load_token, save_token, getfile
from .features import download_works, download_bookmarks, auth


def login(api_object):
    """
    用于登录api,使用简单的base85加密储存token
    :param api_object: api对象
    :return: 无
    """
    if os.path.exists('token.txt'):
        print('您登陆过，正在验证...')
        tokens = load_token()
        tokens = auth(api_object,
                      access_token=tokens['access_token'],
                      refresh_token=tokens['refresh_token'])
        if tokens:
            print('登陆成功！')
            save_token(tokens)

        # 如果token失效，那么就删除token.txt重新验证
        else:
            print('旧的登录信息已经失效，请重新用用户名密码登录')
            os.remove('token.txt')
            login(api_object)

    else:
        print('请输入用户名(或邮箱地址)和密码来登录')
        username = input('请输入用户名(或邮箱地址):')
        password = getpass.getpass('请输入密码:')
        tokens = auth(api_object,
                      username=username,
                      password=password)
        if tokens:
            print('登陆成功!')
            save_token(tokens)

        # 如果api返回错误，就重新登录
        else:
            print('登陆失败或网络状况不好，请重新登录!')
            login(api_object)

def work(api_object):
    """
    确定工作模式并工作
    :return: 
    """
    while True:
        mode = input('请输入工作模式(1是下载画师作品,2是下载收藏夹):')
        if mode in ['1', '2', '3']:
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

    # Test Mode
    if mode == '3':
        print(getfile('13665349'))