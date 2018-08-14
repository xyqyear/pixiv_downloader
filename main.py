# -*- encoding:utf-8 -*-

from resources import back_end, protocol
from multiprocessing.dummy import current_process
from PyQt5.QtWidgets import QApplication

import sys
if sys.argv[1:]:
    cmd = sys.argv[1]
    if cmd == "cmd":
        from resources import cmd_front_end as front_end
    elif cmd == "gui":
        from resources import gui_front_end as front_end
else:
    from resources import gui_front_end as front_end


if __name__ == "__main__":
    (front_pipe, back_pipe) = protocol.ProtocolPipe()()
    process = current_process()

    app = QApplication(sys.argv[2:])

    Front = front_end.FrontEnd(front_pipe, process)
    Back = back_end.BackEnd(back_pipe, process)

    thread_list = [Front, Back]
    for t in thread_list:
        t.start()

    sys.exit(app.exec_())
    # 只等待前端关闭就行了

