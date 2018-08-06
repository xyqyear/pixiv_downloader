# coding = utf-8

import getpass
import base64
import json
import os

from .managers import token_holder
from .utils import exception_handler

token_file = "token.txt" # 默认存储token 位置

class user_manager():

    def login(self, api_object):
        if os.path.exists(token_file):
            print("您登陆过，正在验证...")
            tokens = token_holder.load(token_file)
            tokens = token_holder.auth(api_object,
                          access_token=tokens['access_token'],
                          refresh_token=tokens['refresh_token'])
            if tokens:
                print('登陆成功！')
                token_holder.save(tokens)
            
            else:
                print('旧的登录信息已经失效，请重新用用户名密码登录')
                os.remove(token_file)
                self.login(api_object)

        else:
            print('请输入用户名(或邮箱地址)和密码来登录')
            username = input('请输入用户名(或邮箱地址): ')
            password = getpass.getpass('请输入密码: ')
            tokens = token_holder.auth(api_object,
                          username=username,
                          password=password)
            if tokens:
                print('登陆成功!')
                token_holder.save(tokens)

            else:
                print('登陆失败或网络状况不好，请重新登录!')
                self.login(api_object)


    

