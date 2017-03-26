# -*- coding: utf-8 -*-
# This file Aim to cut the ROI area of the lung, which can reduce the area have to learn in the data set
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
from skimage import morphology
from skimage import measure
from sklearn.cluster import KMeans
from skimage.transform import resize


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




#if not os.path.exists(OUTPUT_FOLDER):
#    os.makedirs(OUTPUT_FOLDER)    

#patients = os.listdir(INPUT_FOLDER)
#patients.sort()
#print(patients)

patients = [
"c67de8fbbe1e58b464334f93a1dd0447",
"c610439ebef643c7fd4b30de8088bb55",
"c5887c21bafb90eb8534e1a632ff2754",
"c4c801ae039ba335fa32df7d84e4decb",
"c3e8db4f544e2d4ecb01c59551eb8ef0",
"c3b05094939cc128a4593736f05eadec",
"c2e546795f1ea2bd7f89ab3b4d13e761",
"c2bdfb6ab5192656b397459648221918",
"c1673993c070080c1d65aca6799c66f8",
"c1673993c070080c1d65aca6799c66f8",
"c0f0eb84e70b19544943bed0ea6bd374",
"c0625c79ef5b37e293b5753d20b00c89",
"c05acf3bd59f5570783138c01b737c3d",
"c020f5c28fc03aed3c125714f1c3cf2a",
"be2be08151ef4d3aebd3ea4fcd5d364b",
"bda661b08ad77afb79bd35664861cd62",
]

PatientPath = INPUT_FOLDER + patients[0]

patientScans = load_scan(PatientPath)
patient_pixels = get_pixels_hu(patientScans)

plt.figure()
plt.title("the img ")
plt.imshow(patient_pixels[60], cmap='gray')


# ---show the histogram 
img = patient_pixels[60]
mean = np.mean(img)
std = np.std(img)
img = img-mean
img = img/std

plt.figure()
plt.title("pixel distribution")
plt.hist(img.flatten(),bins=200)

# threshold the img

img = patient_pixels[60]
middle = img[100:400,100:400] 
mean = np.mean(middle)  
max = np.max(img)
min = np.min(img)
#move the underflow bins
img[img==max]=mean
img[img==min]=mean
kmeans = KMeans(n_clusters=2).fit(np.reshape(middle,[np.prod(middle.shape),1]))
centers = sorted(kmeans.cluster_centers_.flatten())
threshold = np.mean(centers)
thresh_img = np.where(img<threshold,1.0,0.0)  # threshold the image

plt.figure()
plt.title("thresh_img")
plt.imshow(thresh_img, cmap='gray')

#Erosion and Dilation 
eroded = morphology.erosion(thresh_img,np.ones([4,4]))
dilation = morphology.dilation(eroded,np.ones([10,10]))
labels = measure.label(dilation)
label_vals = np.unique(labels)
plt.figure()
plt.title("Erosion and Dilation ")
plt.imshow(labels)
                     

# cut roi
labels = measure.label(dilation)
label_vals = np.unique(labels)
regions = measure.regionprops(labels)
good_labels = []
for prop in regions:
    B = prop.bbox
    if B[2]-B[0]<475 and B[3]-B[1]<475 and B[0]>40 and B[2]<472:
        good_labels.append(prop.label)
mask = np.ndarray([512,512],dtype=np.int8)
mask[:] = 0
#
#  The mask here is the mask for the lungs--not the nodes
#  After just the lungs are left, we do another large dilation
#  in order to fill in and out the lung mask 
#
for N in good_labels:
    mask = mask + np.where(labels==N,1,0)
mask = morphology.dilation(mask,np.ones([10,10])) # one last dilation
plt.figure()
plt.title("Cutting non-ROI Regions ")
plt.imshow(mask,cmap='gray')

# mask img 
img = patient_pixels[60]
masked_img = mask*img

plt.figure()
plt.title("Masked")
plt.imshow(masked_img,cmap='gray')