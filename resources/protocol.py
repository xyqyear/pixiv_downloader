# coding = utf-8

from multiprocessing.dummy import Pipe


# 实现了一个小型的前后端通讯协议
# 管道主体
class ProtocolPipe:

    def __init__(self):
        # 通过实例化一个multiprocessing 的pipe 以获得两个通讯端
        (self.p0, self.p1) = Pipe()
        # 将通讯端包装上协议需要的功能
        self.c0 = Connection(self.p0)
        self.c1 = Connection(self.p1)

    # 向外界递送此管道的通讯端
    def connections(self):
        return self.c0, self.c1


# 包装通讯端功能
class Connection:

    def __init__(self, connection):
        self.connection = connection

    # 将pipe 的recv 方法包装上解包功能
    def get(self):
        pack = self.connection.recv()
        value = pack.value
        sender = pack.sender
        value_type = pack.value_type
        return {"value": value, "sender": sender, "value_type": value_type}

    # 将发送的数据包装上数据类型
    def set(self, value, sender=None, value_type=None):
        pack = Pack(value, sender, value_type)
        self.connection.send(pack)

    # require 用于索要数据
    def require(self, require, sender, value_type="require"):
        self.set(require, sender, value_type)
        data = self.get()
        return data

    # report 用于报告状态
    def report(self, status_type, status, sender, value_type="status"):
        info = {"status_type": status_type, "status": status}
        self.set(info, sender, value_type)

    # 传送调试信息
    # 便于方便地去除调试信息
    def debug(self, value, sender, value_type="debug"):
        self.set(value, sender, value_type)


class Pack:

    def __init__(self, value, sender, value_type):
        self.value = value
        self.sender = sender
        self.value_type = value_type if value_type else "data"


if __name__ == "__main__":
    pipe = ProtocolPipe()
    (p0, p1) = pipe.connections()
    p0.set("try display something", "command")
    print(p1.get())
