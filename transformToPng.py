# -*- coding: utf-8 -*-


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
import gc
import scipy.misc


from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Some constants 
INPUT_FOLDER = './stage1/' #'./stage1/'
OUTPUT_FOLDER = './stage1_jpg/'#"./pngFormat/"


# Load the scans in given folder path
def load_scan(path):
    slices = [dicom.read_file(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
        
    for s in slices:
        s.SliceThickness = slice_thickness
        
    return slices



def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16), 
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    
    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
            
        image[slice_number] += np.int16(intercept)
    
    return np.array(image, dtype=np.int16)


def transformPatientScan(PatientPath, patientName):
    
    
    directory = OUTPUT_FOLDER+ patientName
    if not os.path.exists(directory):
        print("start process "+patientName)
        start = timeit.default_timer()
        patientScans = load_scan(PatientPath)
        patient_pixels = get_pixels_hu(patientScans)
        os.makedirs(directory)    
        for i in range(len(patient_pixels)):
#            start_ = timeit.default_timer()
            scipy.misc.imsave(directory+"/"+'{:03d}'.format(i)+'.jpg', patient_pixels[i])
#            stop_ = timeit.default_timer()
#            print stop_ - start_
        print(patientName + " used "+ str(timeit.default_timer() - start  ) )
        del patient_pixels
        del patientScans
        gc.collect()



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



if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)    

patients = os.listdir(INPUT_FOLDER)
patients.sort()
print(patients)

#patients = [
#"c67de8fbbe1e58b464334f93a1dd0447",
#"c610439ebef643c7fd4b30de8088bb55",
#"c5887c21bafb90eb8534e1a632ff2754",
#"c4c801ae039ba335fa32df7d84e4decb",
#"c3e8db4f544e2d4ecb01c59551eb8ef0",
#"c3b05094939cc128a4593736f05eadec",
#"c2e546795f1ea2bd7f89ab3b4d13e761",
#"c2bdfb6ab5192656b397459648221918",
#"c1673993c070080c1d65aca6799c66f8",
#"c1673993c070080c1d65aca6799c66f8",
#"c0f0eb84e70b19544943bed0ea6bd374",
#"c0625c79ef5b37e293b5753d20b00c89",
#"c05acf3bd59f5570783138c01b737c3d",
#"c020f5c28fc03aed3c125714f1c3cf2a",
#"be2be08151ef4d3aebd3ea4fcd5d364b",
#"bda661b08ad77afb79bd35664861cd62",
#]


_args_list = []

for i in range(len(patients)):
    _args_list.append([INPUT_FOLDER + patients[i], patients[i]])

pool = ThreadPool(15)
pool.map(transformPatientScan, _args_list)
pool.wait_completion()
print(" --------------  done all ---------------------------------")

    