# -*- coding:utf-8 -*-

from .utils import exception_handler

class token_holder():

    def parse_token_response(token_json):
        """
        从auth方法返回值中解析出token
        :param token_json: 
        :return: 
        """
        return {'access_token':token_json['response']['access_token'],
                'refresh_token':token_json['response']['refresh_token']}

    def save(tokens_dict):
        """
        保存token到文件
        :param tokens_dict: 
        :return: 
        """
        with open('token.txt', 'wb') as f:
            token_json = json.dumps(tokens_dict)
            f.write(base64.b85encode(token_json.encode('utf-8')))

    def load(token_file):
        """
        从文件中读取token
        :return: 
        """
        with open(token_file, 'rb') as f:
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
                exception_handler.raise_exception()
                print('验证已过期,正在刷新')
                tokens = auth(api_object, refresh_token=refresh_token)

        # 如果只传入了refresh_token就用这个验证
        elif refresh_token:
            try:
                new_tokens = api_object.auth(refresh_token=refresh_token)
                tokens = parse_token_response(new_tokens)

            except:
                exception_handler.raise_exception()
                print('用于刷新的token也过期了')
                tokens = None

        # 2333 啥都没传的情况
        else:
            tokens = None

        return tokens

class url_manager():
    
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
