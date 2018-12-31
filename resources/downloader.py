# -*- coding:utf-8 -*-
import requests
import time
import sys
import re
import os

from .utils import ExceptionHandler, FileHandler, ProcessAnimationMaker, print_end, TIMEOUT
from .managers import UrlManager


class Download:

    def bookmarks(self, api_object, user_uid):
        """
        下载收藏夹
        :param api_object: api对象
        :param user_uid: 用户id
        :return:
        """
        while True:
            try:
                user_info = api_object.user_detail(user_uid)
            except:
                ExceptionHandler.raise_exception()
                continue
            break

        # 如果api返回没有profile就说明此用户不存在
        if 'profile' not in user_info:
            print('此用户不存在!')
            return
        user_total_bookmarks = user_info['profile']['total_illust_bookmarks_public']
        user_name = user_info['user']['name']
        # 创建的文件夹名
        prefix = '_'.join([FileHandler.handle_filename(user_name), '收藏夹', user_uid])
        self.check_prefix(prefix)
        print('正在拉取收藏夹列表...')
        max_bookmark_id = str()
        image_urls = list()

        while True:
            try:
                response = api_object.user_bookmarks_illust(user_uid, max_bookmark_id=max_bookmark_id)
            except:
                ExceptionHandler.raise_exception()
                print('此页网络错误，正在重试')
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                max_bookmark_id = api_object.parse_qs(response['next_url'])['max_bookmark_id']
                percentage = int((len(image_urls)/user_total_bookmarks)*100)
                print(f'{percentage}% ', end=print_end)
                sys.stdout.flush()

            else:
                urls = self.check_images(image_urls, prefix)
                print(f'拉取完成')
                break

        self.download_images(urls, prefix)

    def works(self, api_object, user_uid):
        """
        下载画师作品
        :param api_object: api对象
        :param user_uid: 画师id
        :return:
        """
        while True:
            try:
                user_info = api_object.user_detail(user_uid)
            except:
                ExceptionHandler.raise_exception()
                continue
            break

        # 如果api返回没有profile就说明此画师不存在
        if 'profile' not in user_info:
            print('此画师不存在!')
            return
        user_total_illusts = user_info['profile']['total_illusts']
        user_name = user_info['user']['name']
        # 创建的文件夹名
        prefix = '_'.join([FileHandler.handle_filename(user_name), '作品', user_uid])
        self.check_prefix(prefix)
        print('正在拉取画师作品列表...')
        offset = 0
        image_urls = list()
        while True:
            try:
                response = api_object.user_illusts(user_uid, offset=offset)
            except:
                print('此页网络错误，正在重试')
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                offset = api_object.parse_qs(response['next_url'])['offset']
                percentage = int((len(image_urls)/user_total_illusts)*100)
                print(f'{percentage}% ', end=print_end)
                sys.stdout.flush()

            else:
                urls = self.check_images(image_urls, prefix)
                print('拉取完成.')
                break

        self.download_images(urls, prefix)

    def ranking(self, api_object, date, mode):
        """
        下载排行榜
        :param api_object:
        :param mode:
        :param date:
        :return:
        """
        # 创建的文件夹名
        prefix = '_'.join([date, mode])
        print('正在拉取排行榜...')
        offset = 0
        image_urls = list()
        animation_maker = ProcessAnimationMaker()

        while True:
            try:
                response = api_object.illust_ranking(date=date, mode=mode, offset=offset)
            except:
                ExceptionHandler.raise_exception()
                print('此页网络错误，正在重试')
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                offset = api_object.parse_qs(response['next_url'])['offset']
                animation_maker.next_action()

            else:
                urls = self.check_images(image_urls, prefix)
                print(f'拉取完成')
                break

        self.download_images(urls, prefix)

    # 以下几个函数是相关联的，就不放在不同的模块里面了
    def download_images(self, urls_list, prefix):
        """
        下载图片列表
        还得检测画师名是不是变了，变了就要改文件夹名字
        :param urls_list: 图片列表，元素都是url组成的list
        :param prefix: 下载的文件夹名
        :return:
        """
        # 如果不存在这个文件夹就创建
        if not os.path.exists(prefix):
            os.makedirs(prefix)

        image_num = sum(len(i) for i in urls_list)
        print(f'即将下载{image_num}张图片')
        download_count = 0

        for bag in urls_list:
            image_id = re.split(r'[/_]', bag[0])[-2]
            # 如果只有一张图片就放在同一层级
            if len(bag) == 1:
                path_prefix = prefix
            # 如果有多张图片则放入文件夹
            else:
                path_prefix = os.path.join(prefix, image_id)
                # 文件夹不存在就创建
                if not os.path.exists(path_prefix):
                    os.makedirs(path_prefix)

            for url in bag:
                image_file_name = os.path.basename(url)
                image_full_path = os.path.join(path_prefix, image_file_name)

                download_count += 1
                display_name = os.path.splitext(image_file_name)[0]
                percentage = 100 * download_count/image_num

                print(f'第{download_count}张图片{display_name}正在下载(总{percentage:.1f}%)', end=print_end)
                sys.stdout.flush()
                if self.real_download(url, image_full_path):
                    print(f'第{download_count}张图片{display_name}下载完成(总{percentage:.1f}%)')
                else:
                    print(f'第{download_count}张图片{display_name}下载失败多次，已跳过下载(总{percentage:.1f}%)')

        print('所有图片下载完成')

    @staticmethod
    def check_prefix(prefix):
        """
        检查画师是否改名了
        如果prefix的后面两个东西存在于子目录名中
        就把那个子目录名字改成新的名字
        :param prefix: 新的文件名
        :return:
        """
        id_and_mode = prefix.split('_', 1)[-1]
        for dir_ in os.listdir('.'):
            if id_and_mode in dir_:
                os.rename(dir_, prefix)

    @staticmethod
    def check_images(urls_list, prefix):
        """
        从列表中去除下载过的图片
        :param urls_list:
        :param prefix:
        :return:
        """
        downloaded_file_name = [os.path.split(i)[1] for i in FileHandler.getfile(prefix)]
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
        return urls_list

    @staticmethod
    def real_download(url, path, retry_count=4):
        """
        下载图片
        :param url:
        :param path:
        :param retry_count: 重试次数
        :return: 完不完成
        """
        for i in range(retry_count):
            try:
                response = requests.get(url, headers={'Referer': 'https://app-api.pixiv.net/'}, timeout=TIMEOUT)
                with open(path, 'wb') as f:
                    f.write(response.content)
                return True
            except:
                time.sleep(1)

        return False
