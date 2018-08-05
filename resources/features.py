# -*- coding:utf-8 -*-
import requests
import time
import sys
import re
import os

from .utils import print_exception, print_end, getfile
from .parsers import parse_image_url

def download_bookmarks(api_object, user_uid):
    """
    下载收藏夹
    :param api_object: api对象
    :param user_uid: 用户id
    :return: 
    """
    while True:
        try:
            user_info = api_object.user_detail(user_uid)
            user_total_bookmarks = user_info['profile']['total_illust_bookmarks_public']
            user_name = user_info
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



# 以下三个函数是相关联的，就不放在不同的模块里面了
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