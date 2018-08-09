# coding = utf-8

from .managers import TokenHolder
from .utils import ExceptionHandler


# 用于登陆账号，与服务器建立连接
class HandShaker:

    def __init__(self, pipe, api):
        self.pipe = pipe
        self.token_holder = TokenHolder()
        self.tokens = None
        self.api_object = api

    def start(self):
        if self.token_holder.exist_token():
            login_strategy = self.require("login_strategy")["value"]
            if login_strategy == "token":
                self.login_with_token()
            elif login_strategy == "password":
                self.login_with_password()
        else:
            self.login_with_password()
        save_token = self.require("token_strategy")["value"]
        print(f"Handshaker got token_strategy: {save_token}")
        if save_token == True:
            self.token_holder.tokens = self.tokens
        else:
            self.token_holder.remove_token()
        return True

    def login_with_token(self):
        self.tokens = self.auth(login_method="token")
        if self.tokens:
            self.pipe.set("登陆成功！", "data")
        else:
            self.pipe.set("旧的登陆信息已经失效，请使用账号密码登录", "data")
            self.token_holder.remove_token()
            self.login_with_password()

    def login_with_password(self):
        self.pipe.set("请输入用户名(或邮箱地址)和密码来登录", "data")
        username = self.require("username")["value"]
        self.pipe.set(f"Handshaker got username: {username}")
        password = self.require("password")["value"]
        self.pipe.set(f"Handshaker got password: {password}")
        self.tokens = self.auth(login_method="password",
                                login_info=(username, password))
        if self.tokens:
            self.pipe.set("登录成功！")
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
                tokens = self.token_holder.tokens
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
                refresh_token = self.token_holder.tokens["refresh_token"]
                new_tokens = self.api_object.auth(refresh_token=refresh_token)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                ExceptionHandler.raise_exception()
                self.pipe.set('用于刷新的token也过期了')
                tokens = None

        else:
            tokens = None

        return tokens

    def require(self, command):
        self.pipe.set(command, "command")
        info = self.pipe.get()
        return info
