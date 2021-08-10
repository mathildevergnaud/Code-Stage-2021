import czifile as czi  # Import of the czilib to read files: pip install czifile
import cv2  # pip install opencv-python
import math


class CarrierOverview:
    """
    This class is aimed at easily retrieving useful metadata
    from a czi file containing a CarrierOverview from the CD7 system
    """

    dir = ''
    filename = ''
    metadata = dict()

    def __init__(self, folder='', file=''):
        """
        Constructor: creates a new CarrierOverviewMetadata object
        :param folder: the folder in which the image is
        :param file: name of the czi image
        """

        self.dir = folder
        self.filename = file
        self.parse_metadata()  # Directly parses the metadata to make them available

    def parse_metadata(self):
        """
        Looks for individual data within the input files and stores them into a dictionary
        """
        czi_file = czi.CziFile(self.dir + self.filename)  # Open file

        # First, stores the relevant metadata from the XML metadata header
        from_xml = czi_file.metadata(raw=False)['ImageDocument']['Metadata']
        '''
            XML metadata structure: stared items are (sub-)dictionaries, dashed items are k, v pairs
            ImageDocument
                Metadata
                    CustomAttributes
                        - NeedsPyramidRecalculation
                    Information
                        Document
                            - UserName
                            - CreationDate
                        Image
                            - SizeX
                            - SizeY
                            - SizeM
                            - OriginalCompressionMethod
                            - OriginalEncodingQuality
                            - Dimensions
                    Scaling
                        - Metadata
                        AutoScaling
                            - Type
                            - CreationDateTime
                        Items
                            - Distance
                    DisplaySetting
                        Channels
                            Channel
                                - BitCountRange
                                - PixelType
                                - DyeName
                                - ColorMode
                                - Id
                                - Name
                        ToneMapping
                            - Mode
                            - EnhanceClipLimit
                            - EnhanceRegionSizePercentage
                        - ViewerRotations
                    - Layers
        '''
        self.metadata['SizeX_pixels'] = from_xml['Information']['Image']['SizeX']
        self.metadata['SizeY_pixels'] = from_xml['Information']['Image']['SizeY']
        self.metadata['SizeM'] = from_xml['Information']['Image']['SizeM']
        self.metadata['EnhanceClipLimit'] = from_xml['DisplaySetting']['ToneMapping']['EnhanceClipLimit']
        self.metadata['EnhanceRegionSizePercentage'] = from_xml['DisplaySetting']['ToneMapping'][
            'EnhanceRegionSizePercentage']

        for element in from_xml['Scaling']['Items']['Distance']:
            self.metadata['Calib' + element['Id'] + '_microns'] = element['Value'] * 1000000.0

        # Second, look for additional metadata from the segments

        # Looks at the image sub blocks within the file
        sub_blocks = czi_file.subblocks()

        for subBlock in sub_blocks:
            bloc_nb = -1

            '''
            Extracts the following infos from the subblock:
            the block number, its start, size, start coordinate and stored size
            once done, everything is pushed to the metadata dictionary with a key in the form:
            TileXX_dimension_parameterName
            '''
            for sub in subBlock.directory_entry.dimension_entries:
                # Lazy way: supposing the M tag will always be present in subblocks BEFORE X or Y blocks
                if sub.dimension == 'M':
                    bloc_nb = sub.start
                else:
                    self.metadata['Tile' + str(bloc_nb) + "_" + sub.dimension + "_start"] = sub.start
                    self.metadata['Tile' + str(bloc_nb) + "_" + sub.dimension + "_size"] = sub.size
                    self.metadata[
                        'Tile' + str(bloc_nb) + "_" + sub.dimension + "_start_coordinate"] = sub.start_coordinate
                    self.metadata['Tile' + str(bloc_nb) + "_" + sub.dimension + "_stored_size"] = sub.stored_size
            '''
            Now the tile number has been extracted, get the stage coordinates and
            pushes to the metadata dictionary with a key in the form TileXX_parameterName_units
            '''
            for key, value in subBlock.metadata(raw=False)['Tags'].items():
                self.metadata['Tile' + str(bloc_nb) + '_' + key + '_mm'] = value / 1000.0

        '''
        Quite tricky to recompute the stage coordinates of the central position...
        First, computes the stage calibration from the two first tiles:
            - Computes the slope delta positions in mm / delta positions in pixels.
        '''
        slope = (self.metadata['Tile1_StageXPosition_mm']-self.metadata['Tile0_StageXPosition_mm'])/(self.metadata['Tile1_X_start']-self.metadata['Tile0_X_start'])
        slope = (int(slope * 10000)) / 10000 # limit to 4 digits because... it seems to work ;-)
        '''
        Second, computes the X/Y stage offset from the first tile:
            - Slope*img_size/2: coordinate of the center of the image relative to the stage if the origin was top-let
            - -start_coordinate: takes into account the offset of the stage (origin is not zero)
            - +tile0_size/2*pixel_size: takes into account the fact that the coordinates are relative to the center of
            the first tile, converting coordinates using the image calibration
        '''
        self.metadata['ImageCenterPosition_X_mm'] = slope*(self.metadata['SizeX_pixels']/2) + self.metadata['Tile0_StageXPosition_mm'] - (self.metadata['Tile0_X_stored_size']/2)*self.metadata['CalibX_microns']/1000
        self.metadata['ImageCenterPosition_X_mm'] = int(self.metadata['ImageCenterPosition_X_mm']*100)/100
        self.metadata['ImageCenterPosition_Y_mm'] = self.metadata['Tile1_StageYPosition_mm']

        czi_file.close()

    def get_image(self):
        """
        Reads the image data and shapes it as a NumPy array
        :return: the image data as a NumPy array
        """
        return czi.imread(self.dir + self.filename)  # Open file as image

    def save_image(self, out_dir='', out_name=''):
        """
        Saves the current image using openCV, the format being automatically adapted,
        depending on the file name's extension
        :param out_dir: the output folder
        :param out_name: the name of the file
        """
        cv2.imwrite(out_dir + out_name, self.get_image())

    def show(self, name='CarrierOverview'):
        """
        Displays the image data in a new window
        :param name: non mandatory parameter, name to be given to the image window
        """
        cv2.imshow(name, self.get_image())
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def __str__(self):
        out = ''
        for key, value in self.metadata.items():
            out += key + ': ' + str(value) + '\n'
        return out
