import threading, time


def doWaiting1():
    print('start waiting1: ' + time.strftime('%H:%M:%S') + "\n")
    time.sleep(2)
    print("线程1奉命报道")
    print('stop waiting1: ' + time.strftime('%H:%M:%S') + "\n")


def doWaiting2():
    print('start waiting2: ' + time.strftime('%H:%M:%S') + "\n")
    time.sleep(8)
    print("线程2奉命报道")
    print('stop waiting2: ', time.strftime('%H:%M:%S') + "\n")


tsk = []

# 创建并开启线程1
thread1 = threading.Thread(target=doWaiting1)
thread1.setDaemon(True)
thread1.start()
tsk.append(thread1)

# 创建并开启线程2
thread2 = threading.Thread(target=doWaiting2)
thread2.setDaemon(True)
thread2.start()
tsk.append(thread2)

print('start join: ' + time.strftime('%H:%M:%S'))
for t in tsk:
    print("开始:" + time.strftime('%H:%M:%S'))
    print('%s线程到了' % t)
    # t.join(5)
    time.sleep(3)
    print("结束:" + time.strftime('%H:%M:%S'))
time.sleep(3)
print('end join: ' + time.strftime('%H:%M:%S'))
