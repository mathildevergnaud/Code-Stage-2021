"""
Pour faire fonctionner cette classe les librairies à uttiliser sont :
    conda install -c menpo opencv
    pip install czifile
    pip install scikit-image
    version python : 3.6

"""


import cv2
from matplotlib import pyplot as plt
import numpy as np
import math
from skimage.morphology import skeletonize
from skimage.transform import probabilistic_hough_line
from skimage import feature

import ReadExperiment

def takeSecond(elem):
    return elem[0]
    
def takeFirst(elem):
    return elem[1]

class Transmission :
    """
    This class is for finding cut and write on the initial image where there are
    """
    
    image_file = ''
    image_ori = ''
    image_in = ''
    ROI = list()
    lines = list()
    
    def __init__(self, path ='tiles_acquisition_stitcher0.czi'):
        """
        Constructor :
        """
        
        self.image_file = ReadExperiment.ReadExperiment(path)
        self.image_in = self.image_file.get_image(1)
        self.box_2 = list()
        

    def get_treshold(self) :
        """
        Apply a treshold to binarise this image with cut value is 0 and backgroud 1
        """
        
        histogram, bin_edges = np.histogram(self.image_in, bins=65535, range=(0, 65535))

        max_value =max(histogram[1000:65535])

        i = 1000
        for j in histogram[i:65535] :
            i= i+1
            if j == max_value:
                indice = i

        pietro_maximoff = int(indice*0.85)
    
        ret,self.image_in = cv2.threshold(self.image_in,pietro_maximoff,65535,cv2.THRESH_BINARY)
        self.image_ori = self.image_in
        

    def CannyFilter(self) :
        """
        Apply the Canny filter to our source picture:
        Erase some noise and smoothes the background
        """
        
        self.image_in  = feature.canny(self.image_in, sigma=0.1)
        
        plt.imshow(self.image_in, 'gray')
        plt.show()

    

    def find_cut(self,i):
        """
        Find cut the Hough Line transforme and write on the image source where there are 
        return: list of coordinates of our cut
        """
        #image_tempo = self.get_contours(i)
        image_tempo = self.image_in[i[1]:i[3], i[0]:i[2]]
        
        lines = probabilistic_hough_line(image_tempo, threshold=40, line_length=280,line_gap=50)
        
        for line in lines:
            p0, p1 = line
            x0 = int(p0[0]) + int(i[0])
            y0 = int(p0[1]) + int(i[1])
            x1 = int(p1[0]) + int(i[0])
            y1 = int(p1[1]) + int(i[1])
            line_0 = x0,y0, x1, y1
            
            self.lines.append(line_0)    
            
                     
        
    def sort_lines(self):
        """
        Sort line to select only line between two cut
        """
        
        sortie = list()
        for line in self.lines :
            x1, y1, x2, y2 = line
            
            if abs(y1-y2) < abs(x1-x2)/2:
                sortie.append(line)
                
        sortie.sort(key = takeFirst)
        sortie.sort(key = takeSecond)
            
        return sortie  
        
    
    def find_ROI(self) :
        """
        Define the Region where we have our section
        """
        image_ROI = self.image_file.get_image(0)
              
        histogram, bin_edges = np.histogram(image_ROI, bins=65535, range=(0, 65535))
       
        max_value =max(histogram[1000:10000])

        i = 1000
        for j in histogram[i:10000] :
            i= i+1
            if j == max_value:
                indice = i

        pietro_maximoff = int(indice*1.1)
        
        ret,image_ROI = cv2.threshold(image_ROI,pietro_maximoff,65535,cv2.THRESH_BINARY)
                
        width = int(image_ROI.shape[1] * 1 / 4)
        height = int(image_ROI.shape[0] * 1 / 4)

        image_ROI = cv2.resize(image_ROI, (width, height))
                
        kernel = np.ones((15, 15), np.uint16)
        image_ROI = cv2.morphologyEx(image_ROI, cv2.MORPH_OPEN, kernel)
        
        kernel = np.ones((10, 10), np.uint16)
        image_ROI = cv2.dilate(image_ROI,kernel,iterations = 8)
               
        image_ROI = image_ROI.astype('uint8')
               
        image_ROI, slides, hierarchy = cv2.findContours(image_ROI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
        backtorgb = cv2.cvtColor(image_ROI,cv2.COLOR_GRAY2RGB)
        
        for slide in slides:
            bbox = cv2.boundingRect(slide)
            x, y, w, h = bbox  # unpacking
            BoxforRoi = (x*4,y*4,(x+w)*4,(y+h)*4)
            if 350 < w < width * 3100 and 350 < h < 3100:
                self.ROI.append(BoxforRoi)
                backtorgb = cv2.rectangle(backtorgb,((x),(y)),(x+w,y+h),(255, 0, 0), 5)
        
        for i in self.ROI: 
            plt.imshow(self.image_in[i[1]:i[3], i[0]:i[2]])
            plt.show()
        
        
    def find_cut_in_find_ROI(self) : 
            
        self.find_ROI()    
                
        self.get_treshold()
        
        self.CannyFilter()
            
        for i in self.ROI: 
            self.find_cut(i)
            
        #lines = self.sort_lines()
        
        backtorgb = self.image_ori
        backtorgb = backtorgb.astype('uint8')
        backtorgb = cv2.cvtColor(backtorgb, cv2.COLOR_GRAY2RGB)
        
        for line in self.lines:
            cv2.line(backtorgb, (int(line[0]), int(line[1])), (int(line[2]), int(line[3])), (255,0,0), 10, cv2.LINE_AA)
               
        plt.imshow(backtorgb)
        plt.show()
        
        
        
#---------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------        
                







