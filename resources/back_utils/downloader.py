# coding = utf-8

import requests
import time
import sys
import re
import os

from .utils import ExceptionHandler, FileHandler, ProcessAnimationMaker
from .managers import UrlManager


class Download:

    def __init__(self, pipe, api):
        self.__name__ = "Download"
        self.pipe = pipe
        self.api = api
        self.stop = False

    def bookmarks(self, user_uid):
        while True:
            try:
                user_info = self.api.user_detail(user_uid)
            except:
                ExceptionHandler.raise_exception()
                continue
            break

        # 如果api返回没有profile就说明此用户不存在
        if 'profile' not in user_info:
            self.pipe.report("user_exist", False, self.__name__)
            return
        user_total_bookmarks = user_info['profile']['total_illust_bookmarks_public']
        user_name = user_info['user']['name']
        # 创建的文件夹名
        prefix = '_'.join([FileHandler.handle_filename(user_name), '收藏夹', user_uid])
        self.check_prefix(prefix)
        self.pipe.report("bookmark_list", "pulling", self.__name__)
        max_bookmark_id = str()
        image_urls = list()

        while True:
            try:
                response = self.api.user_bookmarks_illust(user_uid, max_bookmark_id=max_bookmark_id)
            except:
                ExceptionHandler.raise_exception()
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                max_bookmark_id = self.api.parse_qs(response['next_url'])['max_bookmark_id']
                percentage = int((len(image_urls)/user_total_bookmarks)*100)
                self.pipe.report("pulling_percentage", percentage, self.__name__)
                sys.stdout.flush()
            else:
                urls = self.check_images(image_urls, prefix)
                self.pipe.report("pulling_finish", True, self.__name__)
                break

        self.download_images(urls, prefix)

    def works(self, user_uid):
        while True:
            try:
                user_info = self.api.user_detail(user_uid)
            except:
                ExceptionHandler.raise_exception()
                continue
            break

        # 如果api返回没有profile就说明此画师不存在
        if 'profile' not in user_info:
            self.pipe.report("painter_exist", False, self.__name__)
            return
        user_total_illusts = user_info['profile']['total_illusts']
        user_name = user_info['user']['name']
        # 创建的文件夹名
        prefix = '_'.join([FileHandler.handle_filename(user_name), '作品', user_uid])
        self.check_prefix(prefix)
        self.pipe.report("painter_list", "pulling", self.__name__)
        offset = 0
        image_urls = list()
        while True:
            try:
                response = self.api.user_illusts(user_uid, offset=offset)
            except:
                ExceptionHandler.raise_exception()
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                offset = self.api.parse_qs(response['next_url'])['offset']
                percentage = int((len(image_urls)/user_total_illusts)*100)
                self.pipe.report("pulling_percentage", percentage, self.__name__)
                sys.stdout.flush()
            else:
                urls = self.check_images(image_urls, prefix)
                self.pipe.report("pulling_finish", True, self.__name__)
                break

        self.download_images(urls, prefix)

    def ranking(self, date, mode):
        # 创建的文件夹名
        prefix = '_'.join([date, mode])
        self.pipe.report("ranking", "pulling", self.__name__)
        offset = 0
        image_urls = list()
        animation_maker = ProcessAnimationMaker()

        while True:
            try:
                response = self.api.illust_ranking(date=date, mode=mode, offset=offset)
            except:
                ExceptionHandler.raise_exception()
                continue
            image_urls += UrlManager.parse_image_urls(response)
            # 如果还有下一页
            if response['next_url']:
                offset = self.api.parse_qs(response['next_url'])['offset']
                animation_maker.next_action()
            else:
                urls = self.check_images(image_urls, prefix)
                self.pipe.report("pulling_finish", True, self.__name__)
                break

        self.download_images(urls, prefix)

    # 以下几个函数是相关联的，就不放在不同的模块里面了
    def download_images(self, urls_list, prefix):
        # 如果不存在这个文件夹就创建
        if not os.path.exists(prefix):
            os.makedirs(prefix)

        image_num = sum(len(i) for i in urls_list)
        self.pipe.report("download_quantity", image_num, self.__name__)
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
                if self.stop:
                    self.pipe.report("download_stop", True, self.__name__)
                    return
                image_file_name = os.path.basename(url)
                image_full_path = os.path.join(path_prefix, image_file_name)

                download_count += 1
                display_name = os.path.splitext(image_file_name)[0]
                percentage = 100 * download_count/image_num

                # 此处修改后将下载百分比移交前端计算
                self.pipe.report(f"downloading new image", {"name":display_name, "count":download_count}, self.__name__)
                if self.real_download(url, image_full_path):
                    self.pipe.report(f"downloading success", True, self.__name__)
                else:
                    self.pipe.report(f"downloading success", False, self.__name__)

        self.pipe.debug("所有图片下载完成", self.__name__)

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
                response = requests.get(url, headers={'Referer': 'https://app-api.pixiv.net/'})
                with open(path, 'wb') as f:
                    f.write(response.content)
                return True
            except:
                time.sleep(0.5)

        return False