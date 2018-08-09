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

    # 将发送的数据包装上数据类型
    def get(self):
        pack = self.connection.recv()
        value_type = pack.value_type
        value = pack.value
        return {"value": value, "value_type": value_type}

    # 将pipe 的recv 方法包装上解包功能
    def set(self, value, value_type=None):
        pack = Pack(value, value_type)
        self.connection.send(pack)


class Pack:

    def __init__(self, value, value_type):
        self.value = value
        self.value_type = value_type if value_type else "data"


if __name__ == "__main__":
    pipe = ProtocolPipe()
    (p0, p1) = pipe.connections()
    p0.set(2, "command")
    print(p1.get())
