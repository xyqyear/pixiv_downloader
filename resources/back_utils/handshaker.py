# -*- encoding:utf-8 -*-

from .managers import TokenHolder
from .utils import ExceptionHandler


class Handshaker:

    def __init__(self, api):
        self.__name__ = "Handshaker"
        self.token_holder = TokenHolder()
        self.tokens = None
        self.api_object = api

        self.exist_token = self.token_holder.exist_token

    def login_with_token(self, tokens=None):
        if tokens:
            self.tokens = tokens
        self.tokens = self.auth(login_method="token")
        if self.tokens:
            return True
        else:
            self.token_holder.remove_token()
            return False

    def login_with_password(self, username, password):
        self.tokens = self.auth(login_method="password",
                                login_info=(username, password))
        if self.tokens:
            return True
        else:
            return False

    def save_token(self, token_strategy):
        if token_strategy:
            self.token_holder.tokens = self.tokens
        else:
            self.token_holder.remove_token()

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
                    raise TokenExpired
            except:
                tokens = self.auth(login_method="refresh")

        elif login_method == "refresh":
            try:
                refresh_token = self.token_holder.tokens["refresh_token"]
                new_tokens = self.api_object.auth(refresh_token=refresh_token)
                tokens = self.token_holder.parse_token_response(new_tokens)
            except:
                tokens = None

        else:
            tokens = None

        return tokens


class TokenExpired(Exception):
    pass

