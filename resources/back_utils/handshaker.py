# coding = utf-8

from .managers import TokenHolder
from .utils import ExceptionHandler


# 用于登陆账号，与服务器建立连接
class HandShaker:

    def __init__(self, pipe, api):
        self.__name__ = "HandShaker"
        self.pipe = pipe
        self.token_holder = TokenHolder()
        self.tokens = None
        self.api_object = api

    def start(self):
        self.pipe.debug("HandShaker start", self.__name__)
        if self.token_holder.exist_token():
            self.pipe.debug("found token", self.__name__)
            login_strategy = self.pipe.require("login_strategy", self.__name__)["value"]
            self.pipe.debug(f"got login_strategy: {login_strategy}", self.__name__)
            if login_strategy == "token":
                self.login_with_token()
            elif login_strategy == "password":
                self.login_with_password()
        else:
            self.pipe.debug("didn't find token", self.__name__)
            self.login_with_password()
        save_token = self.pipe.require("token_strategy", self.__name__)["value"]
        self.pipe.debug(f"got token_strategy: {save_token}", self.__name__)
        if save_token == True:
            self.token_holder.tokens = self.tokens
        else:
            self.token_holder.remove_token()

    def login_with_token(self):
        self.tokens = self.auth(login_method="token")
        if self.tokens:
            self.pipe.report("login_success", True, self.__name__)
        else:
            self.pipe.report("login_success", False, self.__name__)
            self.token_holder.remove_token()
            self.pipe.debug("removed token", self.__name__)
            self.login_with_password()

    def login_with_password(self):
        self.pipe.report("login_method", "password", self.__name__)
        username = self.pipe.require("username", self.__name__)["value"]
        self.pipe.debug(f"got username: {username}", self.__name__)
        password = self.pipe.require("password", self.__name__)["value"]
        self.pipe.debug(f"got password: {password}", self.__name__)
        self.tokens = self.auth(login_method="password",
                                login_info=(username, password))
        if self.tokens:
            self.pipe.report("login_success", True, self.__name__)
        else:
            self.pipe.report("login_success", False, self.__name__)
            self.login_with_password()

    # 登录并返回token
    def auth(self, login_method=None, login_info=None):
        if login_method == "password":
            self.pipe.debug("try login with password", self.__name__)
            try:
                new_tokens = self.api_object.login(*login_info)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                tokens = None

        elif login_method == "token":
            self.pipe.debug("try login with token", self.__name__)
            try:
                tokens = self.token_holder.tokens
                self.api_object.set_auth(tokens["access_token"],
                                         tokens["refresh_token"])
                if 'error' in self.api_object.illust_follow():
                    raise Exception
            except:
                ExceptionHandler.raise_exception()
                self.pipe.report("token_expire", True, self.__name__)
                tokens = self.auth(login_method="refresh")

        elif login_method == "refresh":
            self.pipe.debug("try refresh token", self.__name__)
            try:
                refresh_token = self.token_holder.tokens["refresh_token"]
                new_tokens = self.api_object.auth(refresh_token=refresh_token)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                ExceptionHandler.raise_exception()
                self.pipe.report("refresh_token_expire", True, self.__name__)
                tokens = None

        else:
            tokens = None

        return tokens
