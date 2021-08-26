import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import ShenCastanFlat as filter
import ReadExperiment

class Decoupe_Image_CZI_To_Jpeg :
    """
    This is to cut a czi image on 256x256 image on jpeg
    """
    
    image_file=""
    input_image=""
    directory = ""
    ROI = list()
    imagette = list()
    list_image = dict()
    
    def __init__(self,directory_file = "",filename = "tiles_acquisition_stitcher0.czi") :
        """
        Constructor :
        """
        self.image_file = ReadExperiment.ReadExperiment(filename)
        self.input_image = self.image_file.get_image(1)
        self.directory = directory_file

    def ShenCastantoBright(self) :
        """
        Apply the ISEF filter to our source picture:
        Erase some noise and smoothes the background
        """
        shanny = filter.ShenCastanFlat(self.input_image)
        self.input_image = shanny.filter()
        
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
            plt.imshow(self.input_image[i[1]:i[3], i[0]:i[2]])
            plt.show()

    def crop(self, image, height = 256, width = 256):
        
        imgwidth, imgheight = image.shape
      
        sizex = int(imgwidth/height)
        sizey = int(imgheight/width)
        imgwidth = height * sizex 
        imgheight = width * sizey

        im_ar = image[0:imgwidth,0:imgheight]

        k = 0
        for i in range(height,imgheight-2*height-1,height):
            for j in range(width,imgwidth-width-1,width):
                #plt.imshow(im_ar[j:j+width,i:i+height])
                #plt.show()
                cc = [j,j+width,i,i+height]
                image_arr = im_ar[j:j+width,i:i+height]
                mpimg.imsave('./image/'+str(i)+'_' + str(k) + '_3image.jpeg', image_arr)
                self.list_image.update({str(i)+'_' + str(k) + '_image.jpeg': cc})
                
                k = k+1
                
        print("done")
            
        return self.list_image
    
    def crop_in_ROI(self):
        
        self.find_ROI()
        self.ShenCastantoBright()
        
        for i in self.ROI: 
            self.imagette.append(self.crop(self.input_image[i[1]:i[3], i[0]:i[2]]))
        
        
        
################################################################################

test = Decoupe_Image_CZI_To_Jpeg()
image = test.crop_in_ROI()
