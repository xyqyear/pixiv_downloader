# coding = utf-8

import base64
import json
import os


# 对token 进行增删改查操作
# 调用应置于handshaker 中
class TokenHolder:

    def __init__(self):
        self.token_file = "token.tkn"

    def parse_token_response(self, token_json):
        """
        从auth方法返回值中解析出token
        :param token_json:
        :return:
        """
        return {'access_token': token_json['response']['access_token'],
                'refresh_token': token_json['response']['refresh_token']}

    def exist_token(self):
        return os.path.exists(self.token_file)

    def remove_token(self):
        if self.exist_token():
            os.remove(self.token_file)

    def _save(self, tokens_dict):
        token_json = json.dumps(tokens_dict)
        encoded_token = base64.b85encode(token_json.encode('utf-8'))
        with open(self.token_file, "wb") as f:
            f.write(encoded_token)

    def _load(self):
        if self.exist_token():
            with open(self.token_file, "rb") as f:
                encoded_token = f.read()
            token_json = base64.b85decode(encoded_token).decode("utf-8")
            tokens_dict = json.loads(token_json)
        else:
            tokens_dict = None
        return tokens_dict

    tokens = property(_load, _save)


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
