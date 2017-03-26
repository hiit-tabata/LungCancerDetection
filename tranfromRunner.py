# -*- coding: utf-8 -*-
import os

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import dicom
import os
import scipy.ndimage
import matplotlib.pyplot as plt
from PIL import Image
from Queue import Queue
import sys
from threading import Thread
import timeit


from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection



class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args[0], args[1])

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()

def myRunner(arg1, arg2):
    cmd = "python transformScan.py " +arg1 +" "+arg2
    print(cmd)
    os.system(cmd)


# Some constants 
INPUT_FOLDER = './stage1/'
patients = os.listdir(INPUT_FOLDER)
patients.sort()
print(patients)


_args_list = []

for i in range(len(patients)):
    _args_list.append([INPUT_FOLDER + patients[i], patients[i]])

pool = ThreadPool(2)
pool.map(myRunner, _args_list)
pool.wait_completion()
print(" --------------  done all ---------------------------------")

    