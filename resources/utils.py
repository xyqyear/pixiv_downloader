# -*- coding:utf-8 -*-
from datetime import timedelta, datetime
import sys
import os

# 某些print的时候用到的end
print_end = '\r'
TIMEOUT = 8000


class FileHandler:

    @staticmethod
    def getfile(dir_, ext=None):
        """
        获取特定路径下面的全部文件的路径
        :param dir_: 文件夹名
        :param ext: 文件后缀名
        :return: 文件路径组成的list
        """
        allfiles = []
        need_ext_filter = (ext is not None)
        for root, dirs, files in os.walk(dir_):
            for files_path in files:
                file_path = os.path.join(root, files_path)
                extension = os.path.splitext(file_path)[1][1:]
                if need_ext_filter and extension in ext:
                    allfiles.append(file_path)
                elif not need_ext_filter:
                    allfiles.append(file_path)
        return allfiles

    @staticmethod
    def handle_filename(string):
        """
        用于处理windows路径敏感的字符串
        :param string: 需要处理的字符串
        :return:
        """
        return string\
            .replace('\\', '_').replace('/', '_') \
            .replace('"', '_').replace('<', '_') \
            .replace('>', '_').replace('|', '_') \
            .replace(':', '_').replace('?', '_').replace('*', '_')


class ExceptionHandler:

    @staticmethod
    def raise_exception():
        """
        打印错误
        :return: 
        """
        f_code_object = sys._getframe(1).f_code
        exception_file_name = os.path.split(f_code_object.co_filename)[1]
        exception_function = f_code_object.co_name
        exception_info = sys.exc_info()
        print(f"Error '{exception_info[1]}' happened on "
              f"file {exception_file_name},"
              f"function {exception_function},"
              f"line {exception_info[2].tb_lineno}")


class ProcessAnimationMaker:

    def __init__(self):
        self.actions = ['-', '\\', '|', '/']
        self.present_action_index = 0

    def next_action(self):
        if self.present_action_index == 3:
            self.present_action_index = 0
        else:
            self.present_action_index += 1
        print(self.actions[self.present_action_index], end=print_end)
        sys.stdout.flush()


def get_yesterday_date():
    yesterday = datetime.today() + timedelta(-1)
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    return yesterday_date
