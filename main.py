# coding = utf-8

from resources import front_end, back_end
import queue

if __name__ == "__main__":

    communicator = queue.Queue(20)

    front = front_end.FrontEnd(communicator)
    back = back_end.BackEnd(communicator)

    thread_list = [front, back]
    for t in thread_list:
        t.start()
