# -*- coding:utf-8 -*-
import base64
import json
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
