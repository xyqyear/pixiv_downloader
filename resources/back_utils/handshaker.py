# coding = utf-8

from pixivpy3 import AppPixivAPI
import base64
import json
import os

from .utils import ExceptionHandler

aapi = AppPixivAPI()


# 用于登陆账号，与服务器建立连接
class HandShaker:

    def __init__(self, pipe):
        self.pipe = pipe
        self.token_file = "token.tkn"
        self.token_holder = TokenHolder(self.token_file)
        self.tokens = self.token_holder.tokens
        self.api_object = aapi

    def start(self):
        if self.token_holder.exist_token():
            login_strategy = self.acquire("login_strategy")["value"]
            if login_strategy == "token":
                self.login_with_token()
            elif login_strategy == "password":
                self.login_with_password()
        else:
            self.login_with_password()
        save_token = self.acquire("token_strategy")["value"]
        if save_token == True:
            self.token_holder.save_token()
        else:
            self.token_holder.remove_token()
        return True

    def login_with_token(self):
        tokens = self.auth(login_method="token")
        if tokens:
            self.pipe.set("登陆成功！", "data")
        else:
            self.pipe.set("旧的登陆信息已经失效，请使用账号密码登录", "data")
            self.token_holder.remove_token()
            self.login_with_password()

    def login_with_password(self):
        self.pipe.set("请输入用户名(或邮箱地址)和密码来登录", "data")
        username = self.acquire("get_username")["value"]
        password = self.acquire("get_password")["value"]
        self.pipe.set(f"Handshaker got login_info: {login_info}")
        tokens = self.auth(login_method="password",
                            login_info=(username, password))
        if tokens:
            self.pipe.set("登陆成功！")
        else:
            self.pipe.set("用户名/密码错误或网络不畅通，尝试重新登录")
            self.login_with_password()

    # 登录并返回token
    def auth(self, login_method=None, login_info=None):
        if login_method == "password":
            try:
                new_tokens = self.api_object.login(*login_info)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                tokens = None

        elif login_method == "token":
            try:
                tokens = self.tokens
                self.api_object.set_auth(tokens["access_token"],
                                         tokens["refresh_token"])
                if 'error' in self.api_object.illust_follow():
                    raise Exception
            except:
                ExceptionHandler.raise_exception()
                self.pipe.set('验证已过期,正在刷新')
                tokens = self.auth(login_method="refresh")

        elif login_method == "refresh":
            try:
                refresh_token = self.tokens["refresh_token"]
                new_tokens = self.api_object.auth(refresh_token=refresh_token)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                ExceptionHandler.raise_exception()
                self.pipe.set('用于刷新的token也过期了')
                tokens = None

        else:
            tokens = None

        return tokens

    def acquire(self, command):
        self.pipe.set(command, "command")
        info = self.pipe.get()
        return info


class TokenHolder:

    def __init__(self, token_file):
        self.token_file = token_file

    def parse_token_response(self, token_json):
        """
        从auth方法返回值中解析出token
        :param token_json:
        :return:
        """
        return {'access_token': token_json['response']['access_token'],
                'refresh_token': token_json['response']['refresh_token']}

    def exist_token(self):
        os.path.exists(self.token_file)

    def remove_token(self):
        if self.exist_token():
            os.remove(self.token_file)

    def _save(self, tokens_dict):
        token_json = json.dumps(tokens_dict)
        encoded_token = base64.b85encode(token_json.encode('utf-8'))
        with open(self.token_file, "wb") as f:
            f.write(encoded_token)

    def _load(self):
        with open(self.token_file, "rb") as f:
            encoded_token = f.read()
        token_json = base64.b85decode(encoded_token).decode("utf-8")
        tokens_dict = json.loads(token_json)
        return tokens_dict

    tokens = property(_load, _save)
