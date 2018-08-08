# coding = utf-8

from resources import front_end, back_end
from multiprocessing.dummy import Pipe, Lock, current_process

if __name__ == "__main__":

    (front_communicator, back_communicator) = Pipe()
    t_lock = Lock()
    process = current_process()

    front = front_end.FrontEnd(front_communicator, t_lock, process)
    back = back_end.BackEnd(back_communicator, t_lock, process)

    thread_list = [front, back]
    for t in thread_list:
        t.start()
