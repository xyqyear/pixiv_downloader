

class Pack:

    def __init__(self, info):
        self.info = info


commands = {"login_info": Pack("get_login_info"),
            "working_mode": Pack("get_working_mode")}