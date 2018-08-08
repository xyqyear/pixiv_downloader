# coding = utf-8

from resources import front_end, back_end
from threading import Lock
from multiprocessing import Pipe

if __name__ == "__main__":

    communicator = Pipe()
    t_lock = Lock()

    front = front_end.FrontEnd(communicator, t_lock)
    back = back_end.BackEnd(communicator, t_lock)

    thread_list = [front, back]
    for t in thread_list:
        t.start()
