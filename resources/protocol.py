# coding = utf-8

# 实现了一个小型的前后端通讯协议
# 后续应加入类型标记以及自动打包，并将调用转移到main 中


class Pack:

    def __init__(self, info):
        self.info = info


commands = {"login_info": Pack("get_login_info"),
            "working_mode": Pack("get_working_mode")}