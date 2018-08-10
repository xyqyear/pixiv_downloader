# coding = utf-8

from multiprocessing.dummy import Process
import re
import getpass


# 前端用于与用户交互
class FrontEnd(Process):

    # 从主程序中获取通讯端口，进程锁，以及得知父进程
    def __init__(self, communicator, t_lock, parent):
        # 线程初始化
        Process.__init__(self)
        self.__name__ = "FrontEnd"
        self.communicator = communicator
        self.lock = t_lock
        self._parent = parent
        # 接收到的后端指令与要做的操作对应表
        self.map_require = {"working_mode": self.get_working_mode,
                            "login_strategy": self.get_login_strategy,
                            "username": self.get_username,
                            "password": self.get_password,
                            "token_strategy": self.get_token_strategy,
                            "user_uid": self.get_user_uid,
                            "painter_uid": self.get_painter_uid,
                            "rank_date": self.get_download_date,
                            "rank_type": self.get_rank_type}

    def run(self):
        self.lock_print("FrontEnd start")
        while True:
            # 等待后端传来指令
            info = self.wait_for_info()
            if info["value_type"] == "require":
                self.lock_print(f"{info['sender']} require {info['value']}")
                self.map_require[info["value"]]()
            elif info["value_type"] == "status":
                status = info["value"]
                self.lock_print(f"Status: \\\\{status['status_type']}: {status['status']}\\\\ from {info['sender']}")
            elif info["value_type"] == "debug":
                self.lock_print(f"Debug: \\*{info['value']}*\\ from {info['sender']}")
            else:
                self.lock_print(info["value"])

    def get_login_strategy(self):
        commands = {"0": "password",
                    "1": "token"}
        self.lock_print("您登录过，是否使用保存的通行证登录？")
        self.lock_print("（本地仅保存登录token， 您的密码不会被保存）")
        while True:
            self.lock_print("0: 重新登录 1: 使用保存的通行证登录  （默认使用通行证登录）")
            command = input()
            if command.isspace() or (not command):
                login_strategy = "token"
                break
            elif command in commands:
                login_strategy = commands[command]
                break
            else:
                self.lock_print("请输入正确的指令")
        self.communicator.set(login_strategy)
        self.lock_print("Frontend sent login_strategy")

    def get_username(self):
        self.lock_print("请输入用户名(或邮箱地址):")
        username = input()
        self.communicator.set(username, "data")
        self.lock_print("Frontend sent username")

    def get_password(self):
        self.lock_print("请输入密码:")
        password = input()  ######## 为方便测试这里使用的是input！！！！
                            ######## 调试完成后务必！！改回getpass.getpass ！！！！
        self.communicator.set(password, "data")
        self.lock_print("Frontend sent password")

    def get_token_strategy(self):
        self.lock_print("是否保留服务器返回的通行证以便下次登录？")
        self.lock_print("0: 不保存 1: 保存  （默认保留通行证）")
        token_strategy = input()
        if token_strategy == "0":
            save_token = False
        else:
            save_token = True
        self.communicator.set(save_token, "data")
        self.lock_print("Frontend sent token_strategy")

    def get_user_uid(self):
        while True:
            self.lock_print("请输入用户uid:")
            user_uid = input()
            if user_uid.isdigit():
                break
            else:
                self.lock_print("请输入正确的用户uid ！")
        self.communicator.set(user_uid)
        self.lock_print("Frontend sent user_uid")

    def get_painter_uid(self):
        while True:
            self.lock_print("请输入画师uid:")
            painter_uid = input()
            if painter_uid.isdigit():
                break
            else:
                self.lock_print("请输入正确的画师uid ！")
        self.communicator.set(painter_uid)
        self.lock_print("Frontend sent painter_uid")

    def get_download_date(self):
        while True:
            self.lock_print("请输入下载日期，格式为 年-月-日(例: 2018-1-1)")
            self.lock_print(" . / - : | 可作为分隔符")
            self.lock_print("直接回车选择前一天的榜单")
            raw_date = input()
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
        self.communicator.set(date)
        self.lock_print(f"Frontend sent date: {date}")

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
            mode_digit = input()
            if mode_digit in modes:
                mode = modes[mode_digit]
                break
            else:
                self.lock_print("请输入正确的模式")
        self.communicator.set(mode)
        self.lock_print("Frontend sent rank_type")

    def get_working_mode(self):
        command_mapping = {"1": "painter",
                           "2": "bookmarks",
                           "3": "ranking"}
        self.lock_print("选择工作模式：")
        while True:
            self.lock_print("1: 下载画师作品  2: 下载收藏夹  3: 下载排行榜")
            command = input()
            if command in command_mapping:
                working_mode = command_mapping[command]
                break
            else:
                self.lock_print("不可识别的指令")
        self.communicator.set(working_mode)
        self.lock_print("Frontend sent working_mode")

    def wait_for_info(self):
        info = self.communicator.get()
        return info

    def lock_print(self, text):
        with self.lock:
            print(text)


def get_yesterday_date():
    from datetime import timedelta, datetime
    yesterday = datetime.today() + timedelta(-1)
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    return yesterday_date
