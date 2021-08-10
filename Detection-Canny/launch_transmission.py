from matplotlib import pyplot as plt

import Transmission
 
#path = "tiles_acquisition_stitcher0.czi"
path = "tiles_acquisition_stitcher2.czi"

image_trans = Transmission.Transmission(path)
image_trans.find_cut_in_find_ROI()
