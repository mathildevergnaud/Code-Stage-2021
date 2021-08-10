import czifile 
import cv2
import numpy as np
import matplotlib.pyplot as plt

class ReadExperiment :
    
    """
    This class is to import some information from metadata and open a czi file : Experiment-xx.czi 
    """
    
    dir = ''
    filename = ''
    metadata = dict()
    input_image = ''

    
    def __init__(self, folder='', file=''):
        """
        Constructor :
        """
        self.dir = folder
        self.filename = file
        self.parse_metadata()  # Directly parses the metadata to make them available

    def parse_metadata(self):
        """
        Looks for individual data within the input files and stores them into a dictionary
        """
        czi_file = czifile.CziFile(self.dir + self.filename)  # Open file
        
        # First, stores the relevant metadata from the XML metadata header
        from_xml = czi_file.metadata(raw=False)['ImageDocument']['Metadata']
        
        """
        XLM métadata structure:
            Image Metadata
                Experiment 
                    ExperimentBlocks
                        AcquisitionBlock
                            SubDimensionSetup
                                RegionsSetup
                                    SampleHolder
                                        TileRegions
                                            CenterPosition
                HardwareSetting
                ImageScalling
                Information
                    Image
                        SizeX
                        SizeY
                Scaling
                    Metadata
                    AutoScaling
                    items
                        Distance Id = "x"
                            Value
                            DefaultUnitFormat
                        Distance Id = "y"
                            Value
                            DefaultUnitFormat
                        Pixel       
        """
        
        for element in from_xml['Scaling']['Items']['Distance']:
            self.metadata['Calib_' + element['Id'] + '_microns'] = element['Value'] * 1000000.0
            
        self.metadata['Center_position'] = from_xml['Experiment']['ExperimentBlocks']['AcquisitionBlock']['SubDimensionSetups']['RegionsSetup']['SampleHolder']['TileRegions']['TileRegion']['CenterPosition']
        self.metadata['Size_x_pix'] = from_xml['Information']['Image']['SizeX']
        self.metadata['Size_y_pix'] = from_xml['Information']['Image']['SizeY']
        
    def get_image(self, i= 0):
        """
        Extract image usefull to detect cutting strip 
        :load input_image: the image data as a NumPy array
        """

        if i != 0 or i != 1:
            i == 0
            
        img = czifile.imread(self.dir + self.filename) 
        self.input_image = img[0,0,0,i,0,:,:,0]
        
        return self.input_image
    
    def show_histogramme(self):
        """
        show the histogramm of self.input_image
        """
        
        histogram, bin_edges = np.histogram(self.input_image, bins=65535, range=(0, 65535))
        
        plt.figure()
        plt.title("Grayscale Histogram")
        plt.xlabel("grayscale value")
        plt.ylabel("pixels")
        plt.xlim([10,65535]) 

        plt.plot(bin_edges[0:-1], histogram)  # <- or here
        plt.show()
        
        
    def show(self):
        """
        Displays the image data in a new window
        """
        plt.imshow(self.input_image, 'gray')
        plt.show()
        
        
    def __str__(self):
        out = ''
        for key, value in self.metadata.items():
            out += key + ': ' + str(value) + '\n'
        return out


"""
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

        
    








