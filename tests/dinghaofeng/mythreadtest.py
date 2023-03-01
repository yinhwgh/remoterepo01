import threading
import time


def sing():
    for i in range(3):
        print("正在唱歌...%d" % i)
        time.sleep(1)


def dance():
    for i in range(3):
        print("正在跳舞...%d" % i)
        time.sleep(1)


def main_process():
    for i in range(5):
        print('---开始%d---:%s' % (i, time.ctime()))

        t1 = threading.Thread(target=sing)
        t2 = threading.Thread(target=dance)
        print('线程t1：', t1)
        print('线程t2：', t2)
        t1.setDaemon(True)
        t1.start()
        t2.setDaemon(True)
        t2.start()

        print('---结束%d---:%s' % (i, time.ctime()))


if "__main__" == __name__:
    main_process()

