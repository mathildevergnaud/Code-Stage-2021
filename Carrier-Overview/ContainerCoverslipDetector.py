import cv2  # pip install opencv-python
import numpy as np

def sort_np(lstr):
    list_out=list(list())
    for i in range(0,len(lstr[0])) :
        lst_tmp=list()
        for j in range(0,len(lstr[0][i])):
            lst_tmp.insert(j,lstr[0][i][j])
        list_out.append(lst_tmp)
    list_out.sort()    
    return list_out

class ContainerCoverslipDetector:
    """
    This class is aimed at finding the containers and coverslips from a CarrierOverview object
    """

    coo = ''
    mask = ''
    containers = []
    coverslips = []

    def __init__(self, carrier_overview=''):
        """
        Constructor: creates a new ContainerCoverslipDetector object
        :param carrier_overview: the CarrierOverview object to work on
        """

        self.coo = carrier_overview

    def preprocess_image(self):
        img = self.coo.get_image()
        bilateral_filter = cv2.bilateralFilter(img, 17, 9, 36)
        self.mask = cv2.adaptiveThreshold(bilateral_filter, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                          255, 0)

    def find_containers(self, width=40, height=86, tolerance=0.05):
        """
        Performs containers detection: rectangle of user-defined width and height will be looked for,
        taking into account the input tolerance (values +/- the tolerance in percents). It returns a dictionary
        containing the found containers and appends them to the self.container class attribute (list).
        :param width: the expected container width in mm (default value: 40mm, corresponding to the 3 slides holder)
        :param height: the expected container height in mm (default value: 86mm, corresponding to the 3 slides holder)
        :param tolerance: tolerance for dimensions expressed in percents (default value: 0.05)
        :return a dictionary containing the found containers
        """
        out = dict()
        self.containers.clear()

        width = width * 1000 / self.coo.metadata['CalibX_microns']
        height = height * 1000 / self.coo.metadata['CalibY_microns']

        if self.mask is not None:
            self.preprocess_image()

        slides, hierarchy = cv2.findContours(self.mask, cv2.RETR_LIST,
                                             cv2.CHAIN_APPROX_SIMPLE)  # Only want the contours, not the hierarchy
        
        for slide in slides:
            bbox = cv2.boundingRect(slide)
            x, y, w, h = bbox  # unpacking
            if width * (1 - tolerance) < w < width * (1 + tolerance) and height * (1 - tolerance) < h < height * (1 + tolerance):
                self.containers.append(bbox)
        
        self.containers.sort()
        for i in range(len(self.containers)):
            out['Container' + str(i)] = {'Coordinates': list(self.containers[i])}

            
        return out

    def find_circular_coverslips(self, diameter=18, tolerance=0.1, limit_to_area = None):
        """
        Performs coverslips detection: rectangle of user-defined diameter will be looked for,
        taking into account the input tolerance (values +/- the tolerance in percents). It returns a dictionary
        containing the found coverslips and appends them to the self.coverslips class attribute (list).
        :param diameter: the expected circular coverslip's diameter in mm (default value: 18mm)
        :param tolerance: tolerance for dimensions expressed in percents (default value: 0.1)
        :param limit to area: limits the detection of the coverslips to a certain image area
        :return a dictionary containing the found coverslips
        """
        index = 0
        out = dict()
        
        radius = (diameter * 1000 / self.coo.metadata['CalibX_microns']) / 2

        if self.mask is not None:
            self.preprocess_image()

        if limit_to_area is None:
            circles = cv2.HoughCircles(self.mask, cv2.HOUGH_GRADIENT, 2, self.mask.shape[1] / 10,
                                       param1=100, param2=65,
                                       minRadius=int(radius * (1 - tolerance)), maxRadius=int(radius * (1 + tolerance)))
        else:
            x, y, w, h = limit_to_area
            circles = cv2.HoughCircles(self.mask[y:y + h, x:x + w], cv2.HOUGH_GRADIENT, 2, self.mask.shape[1] / 10,
                                       param1=100, param2=65,
                                       minRadius=int(radius * (1 - tolerance)), maxRadius=int(radius * (1 + tolerance)))

        if circles is not None:
            circles = np.uint16(np.around(circles))
            circle = sort_np(circles)

            for crcl in circle[0:]:
                if limit_to_area is not None:
                    x, y, w, h = limit_to_area
                    crcl[0]= crcl[0] + x
                    crcl[1] = crcl[1] + y
                self.coverslips.append(crcl)
                out['Coverslip'+str(index)] = list(crcl)
                index = index+1
                 
        return out

    def find_circular_coverslips_in_containers(self, width_container=40, height_container=86, tolerance_container=0.05, diameter_coverslip=18, tolerance_coverslip=0.1):
        """
        Performs coverslips detection: rectangle of user-defined diameter will be looked for,
        taking into account the input tolerance (values +/- the tolerance in percents)
        :param width_container: the expected container width in mm (default value: 40mm, corresponding to the 3 slides holder)
        :param height_container: the expected container height in mm (default value: 86mm, corresponding to the 3 slides holder)
        :param tolerance_container: tolerance for dimensions expressed in percents (default value: 0.05)
        :param diameter_coverslip: the expected circular coverslip's diameter in mm (default value: 18mm)
        :param tolerance_coverslip: tolerance for dimensions expressed in percents (default value: 0.1)
        :return a dictionary containing the found containers and coverslips taking this shape:
                {Container1:
                    {'Coordinates': [x, y, w, h],
                    'Coverslips': {'Coverslip1': [w, y, radius],
                                   'Coverslip2': [w, y, radius]},
                    }
                 Container2:
                    {'Coordinates': [x, y, w, h],
                    'Coverslips': {'Coverslip1': [w, y, radius],
                                   'Coverslip2': [w, y, radius]}
                    }
                }
        """
        self.coverslips.clear()
        
        out = self.find_containers(width_container, height_container, tolerance_container)
        
        for key, value in out.items():
            coverslips = self.find_circular_coverslips(diameter_coverslip, tolerance_coverslip, limit_to_area=value['Coordinates'])
            out[key]['Coverslips']=coverslips
        
    

    def get_image(self):
        """
        Generates and returns an image superimposing all detections (containers and coverslips)
        over the original image. NB: locations for containers/coverslips are taken from the class attributes, with no
        aspect of hierarchy between them. Detection should have been performed BEFORE calling get_image in order to feed
        the two class attributes.
        :return: the original image overlaid with all detections
        """
        img = cv2.cvtColor(self.coo.get_image(), cv2.COLOR_GRAY2RGB)

        for container in self.containers:
            x, y, w, h = container  # unpacking
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)

        for coverslip in self.coverslips:
            center = (coverslip[0], coverslip[1])
            # circle center
            cv2.circle(img, center, 3, (255, 0, 0), 5)
            # circle outline
            radius = coverslip[2]
            cv2.circle(img, center, radius, (255, 0, 0), 5)

        return img

    def show(self, name='Detections'):
        """
        Displays the image data in a new window
        :param name: non mandatory parameter, name to be given to the image window
        """
        cv2.imshow(name, self.get_image())
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite('image_contener.jpg', self.get_image())

    def test_detect(self):
        img = self.coo.get_image()
        img_out = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2RGB)
        bilateral_filter = cv2.bilateralFilter(img, 17, 9, 36)
        adaptive_thr = cv2.adaptiveThreshold(bilateral_filter, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                             255, 0)
        # edges = cv2.Canny(adaptive_thr, 0, 0)

        # -----------------------------------------------------
        circles = cv2.HoughCircles(adaptive_thr, cv2.HOUGH_GRADIENT, 2, img.shape[1] / 10,
                                   param1=100, param2=65,
                                   minRadius=150, maxRadius=200)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                # circle center
                cv2.circle(img_out, center, 3, (255, 0, 0), 5)
                # circle outline
                radius = i[2]
                cv2.circle(img_out, center, radius, (255, 0, 0), 5)
        # -----------------------------------------------------
        slides, hierarchy = cv2.findContours(adaptive_thr, cv2.RETR_LIST,
                                             cv2.CHAIN_APPROX_SIMPLE)  # Only want the contours, not the hierarchy

        for slide in slides:
            bbox = cv2.boundingRect(slide)
            x, y, w, h = bbox  # unpacking
            if 800 < w < 1000 and 1800 < h < 2000:
                cv2.rectangle(img_out, (x, y), (x + w, y + h), (0, 255, 0), 5)

        zoom = 0.15
        w = int(img.shape[1] * zoom)
        h = int(img.shape[0] * zoom)
        offset_x = 0
        offset_y = 0

        cv2.imshow('Ori', img)
        cv2.imshow('Bilateral_filter', bilateral_filter)
        cv2.imshow('Adaptive_threshold', adaptive_thr)
        # cv2.imshow('Edges', edges)
        cv2.imshow('Detections', img_out)

        cv2.namedWindow('Ori', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Bilateral_filter', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Adaptive_threshold', cv2.WINDOW_NORMAL)
        # cv2.namedWindow('Edges', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Detections', cv2.WINDOW_NORMAL)

        cv2.resizeWindow('Ori', w, h)
        cv2.resizeWindow('Bilateral_filter', w, h)
        cv2.resizeWindow('Adaptive_threshold', w, h)
        # cv2.resizeWindow('Edges', w, h)
        cv2.resizeWindow('Detections', w, h)

        offset_x = offset_x + w
        cv2.moveWindow('Bilateral_filter', offset_x, offset_y)
        offset_x = offset_x + w
        cv2.moveWindow('Adaptive_threshold', offset_x, offset_y)
        offset_x = offset_x + w
        # cv2.moveWindow('Edges', offset_x, offset_y)
        # offset_x = 0
        # offset_y = offset_y + h
        cv2.moveWindow('Detections', offset_x, offset_y)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
