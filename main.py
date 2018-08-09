# coding = utf-8

# 从资源文件夹加载前端和后端文件
from resources import front_end, back_end, protocol
from multiprocessing.dummy import Pipe, Lock, current_process
# Pipe 用于前后端之间通讯 以及下载进程通报下载进度
# Pipe 应当在后续版本进行优化以实现分辨命令类型
# Lock 用于进程加锁，实际应用主要是实现不被打断地打印调试信息
# current_process 这个只是multiprocessing 实例化时必须要知道自己的_parent 是谁
# 真是奇怪的特性

if __name__ == "__main__":
    # 创建pipe 通道，通讯端口分别分配给前后端
    pipe = protocol.ProtocolPipe()
    (front_communicator, back_communicator) = pipe.connections()
    # 实例化进程锁. 在主程序中实例化以便所有进程使用同一个锁
    t_lock = Lock()
    # 获取当前进程名，作为parent_process 传给前后端进程
    process = current_process()

    # 实例化前后端 以及启动进程
    front = front_end.FrontEnd(front_communicator, t_lock, process)
    back = back_end.BackEnd(back_communicator, t_lock, process)

    thread_list = [front, back]
    for t in thread_list:
        t.start()
