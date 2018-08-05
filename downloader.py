# -*- coding:utf-8 -*-
from pixivpy3 import AppPixivAPI
import requests
import getpass
import base64
import json
import time
import sys
import os
import re

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

def login(api_object):
    """
    用于登录api,使用简单的base85加密储存token
    :param api_object: api对象
    :return: 无
    """
    if os.path.exists('token.txt'):
        print('您登陆过，正在验证...')
        tokens = load_token()
        tokens = auth(api_object,
                      access_token=tokens['access_token'],
                      refresh_token=tokens['refresh_token'])
        if tokens:
            print('登陆成功！')
            save_token(tokens)

        # 如果token失效，那么就删除token.txt重新验证
        else:
            print('旧的登录信息已经失效，请重新用用户名密码登录')
            os.remove('token.txt')
            login(api_object)

    else:
        print('请输入用户名(或邮箱地址)和密码来登录')
        username = input('请输入用户名(或邮箱地址):')
        password = getpass.getpass('请输入密码:')
        tokens = auth(api_object,
                      username=username,
                      password=password)
        if tokens:
            print('登陆成功!')
            save_token(tokens)

        # 如果api返回错误，就重新登录
        else:
            print('登陆失败或网络状况不好，请重新登录!')
            login(api_object)

def download_works(api_object, user_uid):
    """
    下载画师作品
    :param api_object: api对象
    :param user_uid: 画师id
    :return: 
    """
    while True:
        try:
            user_total_illusts = api_object.user_detail(user_uid)['profile']['total_illusts']
        except:
            print_exception()
            continue
        break

    print('正在拉取画师作品列表...')
    offset = 0
    image_urls = list()
    while True:
        try:
            response = api_object.user_illusts(user_uid, offset=offset)
        except:
            print('此页网络错误，正在重试')
            continue
        image_urls += parse_image_url(response)
        # 如果还有下一页
        if response['next_url']:
            offset = api_object.parse_qs(response['next_url'])['offset']
            percentage = int((len(image_urls)/user_total_illusts)*100)
            print(f'{percentage}% ', end=print_end)
            sys.stdout.flush()

        else:
            print('100%')
            break

    download_images(image_urls, user_uid)

def download_bookmarks(api_object, user_uid):
    """
    下载收藏夹
    :param api_object: api对象
    :param user_uid: 用户id
    :return: 
    """
    while True:
        try:
            user_total_bookmarks = api_object.user_detail(user_uid)['profile']['total_illust_bookmarks_public']
        except:
            print_exception()
            continue
        break

    print('正在拉取收藏夹列表...')
    max_bookmark_id = str()
    image_urls = list()

    while True:
        try:
            response = api_object.user_bookmarks_illust(user_uid, max_bookmark_id=max_bookmark_id)
        except:
            print_exception()
            print('此页网络错误，正在重试')
            continue
        image_urls += parse_image_url(response)
        # 如果还有下一页
        if response['next_url']:
            max_bookmark_id = api_object.parse_qs(response['next_url'])['max_bookmark_id']
            percentage = int((len(image_urls)/user_total_bookmarks)*100)
            print(f'{percentage}% ', end=print_end)
            sys.stdout.flush()

        else:
            print('100%')
            break

    download_images(image_urls, user_uid)

def download_images(urls_list, prefix):
    """
    下载图片列表
    :param urls_list: 图片列表，元素都是url组成的list
    :param prefix: 下载的文件夹名
    :return:
    """
    # 如果不存在这个文件夹就创建
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    check_images(urls_list, prefix)
    length = len(urls_list)
    for i in range(length):
        image = urls_list[i]
        percentage = int((i/length)*100)
        if len(image) == 1:
            url = image[0]

            image_id = re.split(r'[/_]', url)[-2]
            image_file_name = os.path.basename(url)
            image_full_path = os.path.join(prefix, image_file_name)

            print(f'{percentage}%:正在下载图片{image_id}', end=print_end)
            sys.stdout.flush()
            if real_download(url, image_full_path):
                print(f'{percentage}%:图片{image_id}下载完成')
            else:
                print(f'{percentage}%:图片{image_id}下载失败多次，取消下载。')

        else:
            for url in image:
                image_id = re.split(r'[/_]', url)[-2]
                prefix_handled = os.path.join(prefix, image_id)
                image_file_name = os.path.basename(url)
                image_full_path = os.path.join(prefix_handled, image_file_name)

                # 文件夹不存在就创建
                if not os.path.exists(prefix_handled):
                    os.makedirs(prefix_handled)

                print(f'{percentage}%:正在下载图片{image_file_name}', end=print_end)
                sys.stdout.flush()
                if real_download(url, image_full_path):
                    print(f'{percentage}%:图片{image_file_name}下载完成')
                else:
                    print(f'{percentage}%:图片{image_file_name}下载失败多次，取消下载。')

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

def work(api_object):
    """
    确定工作模式并工作
    :return: 
    """
    while True:
        mode = input('请输入工作模式(1是下载画师作品,2是下载收藏夹):')
        if mode in ['1', '2', '3']:
            break
        print('请重新输入!')

    if mode == '1':
        while True:
            uid = input('请输入画师uid:')
            if uid.isdigit():
                break
            print('请输入正确的画师uid!')

        download_works(api_object, uid)

    if mode == '2':
        while True:
            uid = input('请输入用户uid:')
            if uid.isdigit():
                break
            print('请输入正确的用户uid!')

        download_bookmarks(api_object, uid)

    # Test Mode
    if mode == '3':
        print(getfile('13665349'))

if __name__ == '__main__':
    aapi = AppPixivAPI()
    login(aapi)
    work(aapi)