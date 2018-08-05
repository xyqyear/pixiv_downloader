# -*- coding:utf-8 -*-
import getpass
import base64
import json
import os

from .parsers import parse_token_response
from .utils import print_exception

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

def save_token(tokens_dict):
    """
    保存token到文件
    :param tokens_dict: 
    :return: 
    """
    with open('token.txt', 'wb') as f:
        token_json = json.dumps(tokens_dict)
        f.write(base64.b85encode(token_json.encode('utf-8')))

def load_token():
    """
    从文件中读取token
    :return: 
    """
    with open('token.txt', 'rb') as f:
        token_json = base64.b85decode(f.read()).decode('utf-8')
        tokens_dict = json.loads(token_json)
    return tokens_dict

def auth(api_object, username = str(), password = str(),
                     access_token = str(), refresh_token = str()):
    """
    登录验证
    第一次登录就只传入用户密码
    完了之后api会返回access_token和refresh_token
    api之后的使用和服务器验证的主要就是access_token
    所以验证完用户名密码下次就只传入access_token和refresh_token就行了
    access_token一段时间后会过期，这样就只传入refresh_token来刷新access_token
    :param api_object: api对象
    :param username: 
    :param password: 
    :param access_token: 
    :param refresh_token: 
    :return: token字典
    """

    # 总之先定义返回值
    tokens = {'access_token':access_token,
              'refresh_token':refresh_token}

    # 如果传入了用户名密码就进行初次登录验证
    # 如果登录出错就认为是用户名密码错误
    if username and password:
        try:
            new_tokens = api_object.login(username, password)
            tokens = parse_token_response(new_tokens)
        except:
            tokens = None

    # 如果传入了access_token和refresh_token就用这个验证
    elif access_token and refresh_token:
        try:
            api_object.set_auth(access_token, refresh_token)
            if 'error' in api_object.illust_follow():
                raise Exception
        except:
            print_exception()
            print('验证已过期,正在刷新')
            tokens = auth(api_object, refresh_token=refresh_token)

    # 如果只传入了refresh_token就用这个验证
    elif refresh_token:
        try:
            new_tokens = api_object.auth(refresh_token=refresh_token)
            tokens = parse_token_response(new_tokens)

        except:
            print_exception()
            print('用于刷新的token也过期了')
            tokens = None

    else:
        tokens = None

    return tokens