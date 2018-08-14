# -*- encoding:utf-8 -*-

from multiprocessing.dummy import Process
import re


class FrontEnd(Process):

    def __init__(self, pipe, parent):
        super(FrontEnd, self).__init__()
        self.daemon = True
        self.pipe = pipe
        self._parent = parent

        self.tokens = None

        self.require_mapping = {"working_mode": self.get_working_mode,
                                "login_strategy": self.get_login_strategy,
                                "username": self.get_username,
                                "password": self.get_password,
                                "token_strategy": self.get_token_strategy,
                                "user_uid": self.get_user_uid,
                                "painter_uid": self.get_painter_uid,
                                "rank_date": self.get_download_date,
                                "rank_type": self.get_rank_type}
        self.data_mapping = {"tokens": self.tokens}

    def run(self):
        while True:
            pack = self.pipe.recv()
            if pack.info_type == "require":
                self.do_require(pack.info)
            elif pack.info_type == "data":
                self.set_data(pack.info)
            elif pack.info_type == "state":
                print(pack.info)

    def do_require(self, info):
        self.require_mapping[info]()

    def set_data(self, info):
        self.data_mapping[info[0]] = info[1]

    def get_working_mode(self):
        command_mapping = {"1": "painter",
                           "2": "bookmarks",
                           "3": "ranking"}
        self.lock_print("选择工作模式：")
        while True:
            self.lock_print("1: 下载画师作品  2: 下载收藏夹  3: 下载排行榜")
            command = self.input_info()
            if command in command_mapping:
                working_mode = command_mapping[command]
                break
            else:
                self.lock_print("不可识别的指令")
        self.pipe.send(working_mode)

    def get_login_strategy(self):
        commands = {"0": "password",
                    "1": "token"}
        self.lock_print("您登录过，是否使用保存的通行证登录？")
        self.lock_print("（本地仅保存登录token， 您的密码不会被保存）")
        while True:
            self.lock_print("0: 重新登录 1: 使用保存的通行证登录  （默认使用通行证登录）")
            command = self.input_info()
            if command.isspace() or (not command):
                login_strategy = "token"
                break
            elif command in commands:
                login_strategy = commands[command]
                break
            else:
                self.lock_print("请输入正确的指令")
        self.pipe.send(login_strategy)

    def get_username(self):
        self.lock_print("请输入用户名(或邮箱地址):")
        username = self.input_info()
        self.pipe.send(username, "data")

    def get_password(self):
        self.lock_print("请输入密码:")
        password = self.input_info()  ######## 为方便测试这里使用的是input！！！！
                            ######## 调试完成后务必！！改回getpass.getpass ！！！！
        self.pipe.send(password, "data")

    def get_token_strategy(self):
        self.lock_print("是否保留服务器返回的通行证以便下次登录？")
        self.lock_print("0: 不保存 1: 保存  （默认保留通行证）")
        token_strategy = self.input_info()
        if token_strategy == "0":
            save_token = False
        else:
            save_token = True
        self.pipe.send(save_token, "data")

    def get_user_uid(self):
        while True:
            self.lock_print("请输入用户uid:")
            user_uid = self.input_info()
            if user_uid.isdigit():
                break
            else:
                self.lock_print("请输入正确的用户uid ！")
        self.pipe.send(user_uid)

    def get_painter_uid(self):
        while True:
            self.lock_print("请输入画师uid:")
            painter_uid = self.input_info()
            if painter_uid.isdigit():
                break
            else:
                self.lock_print("请输入正确的画师uid ！")
        self.pipe.send(painter_uid)

    def get_rank_type(self):
        modes = {'0': 'day', '3': 'week', '6': 'month',
                 '7': 'week_rookie', '8': 'week_original',
                 '9': 'day_male', '10': 'day_female',
                 '11': 'day_manga', '12': 'week_manga', '13': 'month_manga',

                 '14': 'day_r18', '15': 'week_r18',
                 '17': 'day_male_r18', '18': 'day_female_r18',
                 '19': 'day_r18_manga', '20': 'week_r18_manga'}
        mapping_list = ["0：日榜", "3：周榜", "6：月榜",
                        "7: 新人 周榜", "8: 原创 周榜", "9：日榜，男性向",
                        "10：日榜，女性向", "11：日榜漫画", "12：周榜漫画",
                        "13：月榜漫画", "14：日榜r18", "15：周榜r18",
                        "17：日榜男性向r18", "19：日榜r18漫画", "20：周榜r18漫画"]
        while True:
            self.lock_print("选择下载榜单，对应表如下: ")
            n_in_raw = 3
            self.lock_print("\t" + "\n\t".join(
                ''.join(map(lambda x: x.ljust(15), mapping_list[i:i+n_in_raw]))
                for i in range(0, len(mapping_list), n_in_raw)))
            mode_digit = self.input_info()
            if mode_digit in modes:
                mode = modes[mode_digit]
                break
            else:
                self.lock_print("请输入正确的模式")
        self.pipe.send(mode)

    def get_download_date(self):
        while True:
            self.lock_print("请输入下载日期，格式为 年-月-日(例: 2018-1-1)")
            self.lock_print(" . / - : | 可作为分隔符")
            self.lock_print("直接回车选择前一天的榜单")
            raw_date = self.input_info()
            if raw_date.isspace() or (not raw_date):
                date = get_yesterday_date()
                break
            parse_date = re.findall(r"(\d{4})[./\-:| ](\d{1,2})[./\-:| ](\d{1,2})",
                                    raw_date)
            if parse_date:
                found_date = parse_date[0]
                (yyyy, mm, dd) = found_date
                date = f"{yyyy}-{mm:0>2}-{dd:0>2}"
                break
            self.lock_print("请输入正确的日期格式")
        self.pipe.send(date)

    def input_info(self):
        info = input()
        return info

    def lock_print(self, *text):
        print(*text)


def get_yesterday_date():
    from datetime import timedelta, datetime
    yesterday = datetime.today() + timedelta(-1)
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    return yesterday_date
