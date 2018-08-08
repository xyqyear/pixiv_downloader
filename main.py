# coding = utf-8

from resources import front_end, back_end
from multiprocessing.dummy import Pipe, Lock

if __name__ == "__main__":

    (front_communicator, back_communicator) = Pipe()
    t_lock = Lock()

    front = front_end.FrontEnd(front_communicator, t_lock)
    back = back_end.BackEnd(back_communicator, t_lock)

    thread_list = [front, back]
    for t in thread_list:
        t.start()
