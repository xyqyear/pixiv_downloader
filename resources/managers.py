# -*- coding:utf-8 -*-

import base64
import getpass
import json
import os

from .utils import ExceptionHandler

token_file = "token.tkn"


class UserManager:

    def __init__(self, api_object):
        self.token_holder = TokenHolder()
        self.api_object = api_object

    def login(self):
        commands = {"0": self.login_with_password,
                    "1": self.login_with_token}
        if os.path.exists(token_file):
            print("您登陆过，是否使用保存的通行证登录？")
            print("(本地仅保存登录token，您的密码不会被保存)")
            while True:
                command = input("0：重新登录 1：使用保存的通行证登录 \n")
                if command in commands:
                    commands[command]()
                    break
                else:
                    print("请输入正确的指令")
        else:
            self.login_with_password()

    def login_with_token(self):
        stored_tokens = self.token_holder.tokens
        tokens = self.token_holder.auth(self.api_object,
                                       access_token=stored_tokens['access_token'],
                                       refresh_token=stored_tokens['refresh_token'])
        if tokens:
            print('登陆成功！')
            self.token_holder.tokens = tokens
        else:
            print('旧的登录信息已经失效，请重新用用户名密码登录')
            os.remove(token_file)
            self.login_with_password()

    def login_with_password(self):
        print('请输入用户名(或邮箱地址)和密码来登录')
        username = input('请输入用户名(或邮箱地址): ')
        password = getpass.getpass('请输入密码: ')
        tokens = self.token_holder.auth(self.api_object,
                                       username=username,
                                       password=password)
        if tokens:
            print('登陆成功!')
            print("是否保存登陆信息?(下次可无需密码直接登录)")
            print("输入数字1 回车以保存. 默认不保存")
            save_token = input()
            if save_token == "1":
                self.token_holder.tokens = tokens
            else:
                if os.path.exists(token_file):
                    os.remove(token_file)
        else:
            print('用户名/密码错误或网络状况不好，请重新登录!')
            self.login_with_password()


class TokenHolder:

    @staticmethod
    def parse_token_response(token_json):
        """
        从auth方法返回值中解析出token
        :param token_json: 
        :return: 
        """
        return {'access_token':token_json['response']['access_token'],
                'refresh_token':token_json['response']['refresh_token']}

    def _save(self, tokens_dict):
        """
        保存token到文件
        :param tokens_dict: 
        :return: 
        """
        with open(token_file, 'wb') as f:
            token_json = json.dumps(tokens_dict)
            f.write(base64.b85encode(token_json.encode('utf-8')))

    def _load(self):
        """
        从文件中读取token
        :return: 
        """
        with open(token_file, 'rb') as f:
            token_json = base64.b85decode(f.read()).decode('utf-8')
            tokens_dict = json.loads(token_json)
        return tokens_dict

    tokens = property(_load, _save)

    def auth(self, api_object, username=str(), password=str(),
                         access_token=str(), refresh_token=str()):
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

        tokens = {'access_token': access_token,
                  'refresh_token': refresh_token}

        # 如果传入了用户名密码就进行初次登录验证
        # 如果登录出错就认为是用户名密码错误
        if username and password:
            try:
                new_tokens = api_object.login(username, password)
                tokens = self.parse_token_response(new_tokens)
            except:
                tokens = None

        # 如果传入了access_token和refresh_token就用这个验证
        elif access_token and refresh_token:
            try:
                api_object.set_auth(access_token, refresh_token)
                if 'error' in api_object.illust_follow():
                    raise Exception
            except:
                ExceptionHandler.raise_exception()
                print('验证已过期,正在刷新')
                tokens = self.auth(api_object, refresh_token=refresh_token)

        # 如果只传入了refresh_token就用这个验证
        elif refresh_token:
            try:
                new_tokens = api_object.auth(refresh_token=refresh_token)
                tokens = self.parse_token_response(new_tokens)

            except:
                ExceptionHandler.raise_exception()
                print('用于刷新的token也过期了')
                tokens = None

        # 2333 啥都没传的情况
        else:
            tokens = None

        return tokens


class UrlManager:

    @staticmethod
    def parse_image_urls(response_json):
        """
        解析返回的画师数据和收藏夹数据
        :param response_json: 
        :return: list:[[url0],[url0,url1]...]
        """
        out_list = list()
        illusts = response_json['illusts']
        for i in illusts:
            urls = list()
            if i['meta_single_page']:
                url = i['meta_single_page']['original_image_url']
                urls.append(url)

            elif i['meta_pages']:
                for page in i['meta_pages']:
                    url = page['image_urls']['original']
                    urls.append(url)

            else:
                continue

            out_list.append(urls)
        return out_list
