# import multiprocessing
# import time
#
#
# def worker(dd, key, item):
#     print("ss")
#     dd[key] = item
#     print(key)
#
#
# if __name__ == "__main__":
#     time_start = time.time()
#     mgr = multiprocessing.Manager()
#     dd = mgr.dict()
#     jobs = [multiprocessing.Process(target=worker, args=(dd, i, i*2)) for i in range(10)]
#
#     for j in jobs:
#         j.start()
#     for j in jobs:
#         j.join()
#     print('results', dd)
#     print("used time = {:.3f}s".format(time.time() - time_start))

import os
from multiprocessing import Process, Manager
from time import sleep

manager = Manager()
q = manager.Queue(maxsize=1)
lock = manager.Lock()   # 初始化一把锁

hh = Manager().Value('i', 9)


def task1():
    global hh
    i = 5
    while i:

        lock.acquire()
        hh.value -= 1
        print('这是任务1.。。。。。。。。。。',os.getpid(),'------',os.getppid(), "hh =", hh.value)
        lock.release()
        sleep(1)
        i -= 1


def task2():
    global hh
    i = 2
    while i:
        lock.acquire()
        hh.value -= 2
        print('这是任务2.。。。。。。。。。。',os.getpid(),'------',os.getppid(), "hh =", hh.value)
        lock.release()
        sleep(2)
        i -= 1


if __name__ == '__main__':
    print(os.getpid())
    # 子进程
    p = Process(target=task1, name='任务1',)
    p.start()

    p1 = Process(target=task2, name='任务2', )
    p1.start()
    p.join()
    p1.join()
    print(p.name)
    print(p1.name)
