
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


from skimage import measure, morphology
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Some constants 
INPUT_FOLDER = './stage1/'
patients = os.listdir(INPUT_FOLDER)
patients.sort()
print(patients)


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
    
    directory = '/media/holman/C870F7FE70F7F154/stage1Processed_/'
    if not os.path.exists(directory):
        os.makedirs(directory)    
    
    directory = '/media/holman/C870F7FE70F7F154/stage1Processed_/'+ patientName
    if not os.path.exists(directory):
        print("start process "+patientName)
        start = timeit.default_timer()
        patientScans = load_scan(PatientPath)
        patient_pixels = get_pixels_hu(patientScans)
        os.makedirs(directory)    
        mplt = plt.figure()
        for i in range(len(patient_pixels)):
            
            start_ = timeit.default_timer()
            plt.imshow(patient_pixels[i], cmap=plt.cm.gray)
            plt.savefig(directory+"/"+'{:03d}'.format(i)+'.png', dpi=900)
            print("saved "+directory+"/"+'{:03d}'.format(i)+'.png')
            mplt.clf()
            stop_ = timeit.default_timer()
            print stop_ - start_
        plt.close(mplt)
        print(patientName + " used "+ str(timeit.default_timer() - start  ) )
        del patient_pixels
        del patientScans
        del mplt
        del start_
        del stop_
        del start
        gc.collect()



#transformPatientScan(sys.argv[0], sys.argv[1])

#
#first_patient = load_scan(INPUT_FOLDER + patients[0])
#first_patient_pixels = get_pixels_hu(first_patient)
#
## Show some slice in the middle
#directory = './sameImg/'+ patients[0]
#if not os.path.exists(directory):
#    os.makedirs(directory)
#
#print(first_patient_pixels[80].shape)
#Image.open('color.png').convert('L').save('bw.png')


#
plt.imshow(first_patient_pixels[80], cmap=plt.cm.gray)
#plt.savefig(directory+"/"+str(80)+'.png', dpi=900)
#plt.show()



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




_args_list = []

for i in range(len(patients)):
    _args_list.append([INPUT_FOLDER + patients[i], patients[i]])

pool = ThreadPool(1)
pool.map(transformPatientScan, _args_list)
pool.wait_completion()
print(" --------------  done all ---------------------------------")

    