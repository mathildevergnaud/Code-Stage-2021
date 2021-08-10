# load and display an image with Matplotlib
import matplotlib
from matplotlib import image
from matplotlib import pyplot as plt
import czifile 
import numpy as np
from PIL import Image
import os
import cv2
import ReadExperiment


class ShenCastanFlat:
    path = ''
    input_image = ''
    radius_param = 64
    flat_param = 4
    alpha_param = 0.25

    kernel_smooth = ''
    convolve_smooth = ''

    kernel_der = ''
    convolve_der_x = ''
    convolve_der_y = ''
    convolve_der_xy = ''
    convolve_der_xy_amplitude = ''
    convolve_der_xy_orientation = ''
    compute_bli = ''
    
    image_contour = ''

    def __init__(self, image):
        """
        initiates a new Shen Castan filtering objects

        Parameters:
            img (2D numpy array): the image to filter
        """
        self.input_image = image
    


    def filter(self, filter_radius=64, flat_radius = 5, alpha=0.6):
        """
        Performs the Shen Castan filtering based on the two input parameters
        Smoothing: h(x)=c.e(-alpha*|x|) with c=(1-e(-alpha))/(1+e(-alpha)
        Derivative: h'(x)=d.e(-alpha*|x|) if x>=0, h'(x)=-d.e(-alpha*|x|) otherwise, with d=1-e(-alpha)

        Parameters:
            filter_radius (float): radius of the filtering window, the kernel will have a length of filter_radius*2+1
            alpha (float): the strength of the smoothing (low value=higher smoothing)

        Return:
            the filtered image (amplitude image), as a numpy array
        """
        self.radius_param = filter_radius
        self.flat_param = flat_radius
        self.alpha_param = alpha

        # Formulas from http://devernay.free.fr/cours/vision/pdf/c3.pdf
        # ------------------------ SMOOTHING ------------------------
        self.kernel_smooth = np.zeros((filter_radius * 2 + 1))
        c = (1 - np.exp(-alpha)) / (1 + np.exp(-alpha))
        kernel_fct = (lambda c_param, alpha_param, x_param: c_param * np.exp(-alpha_param * np.fabs(x_param)))
        for x in range(-filter_radius, filter_radius + 1, 1):
            self.kernel_smooth[x + filter_radius] = kernel_fct(c, alpha, x)
            if -flat_radius <= x <= flat_radius:
                self.kernel_smooth[x + filter_radius] = kernel_fct(c, alpha, 0)

        self.convolve_smooth = self.convolve_2d(self.input_image, self.kernel_smooth, 'xy')
        
        # ------------------------ DERIVATIVE ------------------------
        self.kernel_der = np.zeros((filter_radius * 2 + 1))
        d = 1 - np.exp(-alpha)
        kernel_fct = (lambda d_param, alpha_param, x_param: d_param * np.exp(
            -alpha_param * np.fabs(x_param)) if x_param >= 0 else -d_param * np.exp(-alpha_param * np.fabs(x_param)))
        for x in range(-filter_radius, filter_radius + 1, 1):
            self.kernel_der[x + filter_radius] = kernel_fct(d, alpha, x)
            if -flat_radius <= x < 0:
                self.kernel_der[x + filter_radius] = -d
            if flat_radius >= x > 0:
                self.kernel_der[x + filter_radius] = d

        self.convolve_der_x = self.convolve_2d(self.convolve_smooth, self.kernel_der, 'x')
        self.convolve_der_y = self.convolve_2d(self.convolve_smooth, self.kernel_der, 'y')

        self.convolve_der_xy_amplitude = np.sqrt(np.square(self.convolve_der_x) + np.square(self.convolve_der_y))

        self.convolve_der_xy_orientation = np.arctan2(self.convolve_der_y, self.convolve_der_x)

        return self.convolve_der_xy_amplitude

    

    def convolve_2d(self, img, kernel, dir='xy'):
        """
        Performs a 2D convolution based on an input 2D numpy matrix and a 1D kernel

        Parameters:
            img (2D numpy array): the image to convolve
            kernel (array): the kernel
            dir (string): the direction(s) of convolution (might be x, y or xy)

        Return:
            the convolved image, as a numpy array
        """

        convolved = ''
        convolved_x = []

        # Convolve along x axis
        if dir.find('x') != -1:
            for i in range(0, img.shape[0], 1):
                convolved_x.append(np.convolve(img[i, :], kernel, mode='same'))

            convolved = np.array(convolved_x)

        # Convolve along y axis
        if dir.find('y') != -1:
            convolved_y = []
            # Initialize convolved in cas only y convolution has been called
            if dir.find('x') == -1:
                convolved = img.copy()

            convolved = np.transpose(convolved)

            for i in range(0, convolved.shape[0], 1):
                convolved_y.append(np.convolve(convolved[i, :], kernel, mode='same'))

            convolved = np.array(convolved_y)
            convolved = np.transpose(convolved)
            

        return convolved
    
    
    def ComputeAdaptativeGradient(self, Row , Col, ws):
        SumOn=0.0
        SumOff=0.0
        NbOn=0
        NbOff=0
    
        for i in range(int(-ws/2), int(ws/2)):
            for j in range(int(-ws/2), int(ws/2)):
            
                if self.convolve_der_xy_amplitude[Row+i][Col+j] > 0 :
                    SumOn = SumOn + self.input_image[Row+i][Col+j]
                    NbOn = NbOn +1
                
                if self.convolve_der_xy_amplitude[Row+i][Col+j] <= 0 :
                    SumOff = SumOff + self.input_image[Row+i][Col+j]
                    NbOff = NbOff +1
       
        AvgOff=0.0
        if SumOff > 0.0 :
            AvgOff=float(SumOff/NbOff)

        AvgOn=0.0
        if SumOn > 0.0 :
            AvgOn=float(SumOn/NbOn)
        
        return (AvgOff-AvgOn)
    
    
    def show_process(self, save_path = ''):
        """
        Generates and displays an output figure with the original, smoothed, derivative x, y, xy images, and plots for 
        both the smoothing and derivating kernels 
        
        Parameters:
            save_path (string): the output path
        """
        tag_alpha = str(np.floor(self.alpha_param*100)/100)

        fig = plt.figure(figsize=(8.25, 11.75))

        ax1 = fig.add_subplot(4, 2, 1)
        ax1.title.set_text('Original image')
        ax1.axis('off')
        ax1.imshow(self.input_image)

        ax2 = fig.add_subplot(4, 2, 2)
        ax2.title.set_text('Smooth\na=' + tag_alpha + "\nrad_flat=" + str(self.flat_param) + "\nrad=" + str(self.radius_param))
        ax2.axis('off')
        ax2.imshow(self.convolve_smooth, 'gray')

        ax3 = fig.add_subplot(4, 2, 3)
        ax3.title.set_text('Derivative X')
        ax3.axis('off')
        ax3.imshow(self.convolve_der_x, 'gray')

        ax4 = fig.add_subplot(4, 2, 4)
        ax4.title.set_text('Derivative Y')
        ax4.axis('off')
        ax4.imshow(self.convolve_der_y, 'gray')

        ax5 = fig.add_subplot(4, 2, 5)
        ax5.title.set_text('Derivative XY\nAmplitude')
        ax5.axis('off')
        ax5.imshow(self.convolve_der_xy_amplitude, 'gray')

        ax5 = fig.add_subplot(4, 2, 6)
        ax5.title.set_text('Derivative XY\nOrientation')
        ax5.axis('off')
        ax5.imshow(self.convolve_der_xy_orientation, 'gray')

        ax7 = fig.add_subplot(4, 2, 7)
        ax7.title.set_text('Kernel smoothing')
        ax7.plot(range(-self.radius_param, self.radius_param + 1, 1), self.kernel_smooth)

        ax8 = fig.add_subplot(4, 2, 8)
        ax8.title.set_text('Kernel derivative')
        ax8.plot(range(-self.radius_param, self.radius_param + 1, 1), self.kernel_der)

        plt.show()

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        im = Image.fromarray(self.convolve_der_xy_amplitude)
        im.save(save_path+'Amplitude_export_a=' + tag_alpha + '_rad=' + str(self.radius_param) + '_flat=' + str(self.flat_param) + '.tif')
        im = Image.fromarray(self.convolve_der_xy_orientation)
        im.save(save_path + 'Orientation_export_a=' + tag_alpha + '_rad=' + str(self.radius_param) + '_flat=' + str(self.flat_param) + '.tif')
        im = Image.fromarray(self.convolve_der_x)
        im.save(save_path + 'Derivative_x_export_a=' + tag_alpha + '_rad=' + str(self.radius_param) + '_flat=' + str(
            self.flat_param) + '.tif')
        im = Image.fromarray(self.convolve_der_y)
        im.save(save_path + 'Derivative_y_export_a=' + tag_alpha + '_rad=' + str(self.radius_param) + '_flat=' + str(
            self.flat_param) + '.tif')
    

