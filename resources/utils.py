# -*- coding:utf-8 -*-
import requests
import base64
import json
import time
import sys
import os

# 某些print的时候用到的end
print_end = '\r'

def getfile(dir_,ext = None):
    """
    获取特定路径下面的全部文件的路径
    :param dir_: 文件夹名
    :param ext: 文件后缀名
    :return: 文件路径组成的list
    """
    allfiles = []
    need_ext_filter = (ext is not None)
    for root,dirs,files in os.walk(dir_):
        for files_path in files:
            file_path = os.path.join(root, files_path)
            extension = os.path.splitext(file_path)[1][1:]
            if need_ext_filter and extension in ext:
                allfiles.append(file_path)
            elif not need_ext_filter:
                allfiles.append(file_path)
    return allfiles

def print_exception():
    """
    打印错误
    :return: 
    """
    e = sys.exc_info()
    print(f"Error '{e[1]}' happened on line {e[2].tb_lineno}")

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

def parse_token_response(token_json):
    """
    从auth方法返回值中解析出token
    :param token_json: 
    :return: 
    """
    return {'access_token':token_json['response']['access_token'],
            'refresh_token':token_json['response']['refresh_token']}

def parse_image_url(response_json):
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

def check_images(urls_list, prefix):
    """
    从列表中去除下载过的图片
    :param urls_list: 
    :param prefix: 
    :return:
    """
    downloaded_file_name = [os.path.split(i)[1] for i in getfile(prefix)]
    to_remove_image = list()
    for image in urls_list:
        to_remove_url = list()
        for url in image:
            image_file_name = os.path.basename(url)
            if image_file_name in downloaded_file_name:
                to_remove_url.append(url)

        for url in to_remove_url:
            image.remove(url)

        if not image:
            to_remove_image.append(image)

    for image in to_remove_image:
        urls_list.remove(image)

def real_download(url, path, retry_count = 4):
    """
    下载图片
    :param url: 
    :param path: 
    :param retry_count: 重试次数
    :return: 完不完成
    """
    for i in range(retry_count):
        try:
            response = requests.get(url, headers={'Referer': 'https://app-api.pixiv.net/'})
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        except:
            time.sleep(1)

    return False

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
