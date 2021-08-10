from CarrierOverview import CarrierOverview as co
from ContainerCoverslipDetector import ContainerCoverslipDetector as cc
import numpy as np


class CoordonneeCoverslip :
    
    """
    meta_img : c'est les informationd dont j'ai besoin issu des metadonnées
    meta_tuile : c'est la où je veux enregistrer les données de chaque tuile

    """
    cood = ''
    coo = ''
    meta_img = []


    
    def __init__(self, coverslip_overview_detector='', carrier_overview = ''):
        self.cood = coverslip_overview_detector
        self.coo = carrier_overview

    def pick_some_metadata(self) :
        
        """
        La classe où l'extrait les informations de la metadatas
        """
        
        #self.meta_img.clear()
        

        #Taille en um d'un pixel
        taille_pix_x_um = self.coo.metadata['CalibX_microns']
        taille_pix_y_um = self.coo.metadata['CalibY_microns']
        
        if  taille_pix_x_um == taille_pix_y_um :
            self.meta_img.append(taille_pix_x_um)
            self.meta_img.append(taille_pix_y_um)

        
        #Taille en pixel de l'image
        taille_img_x_pix = self.coo.metadata['SizeX_pixels']
        taille_img_y_pix = self.coo.metadata['SizeY_pixels']
        
        #Taille en um du centre de l'image
        image_centre_um_x= self.coo.metadata['ImageCenterPosition_X_mm']*1000
        image_centre_um_y= self.coo.metadata['ImageCenterPosition_Y_mm']*1000

        #Coin en haut à gauche de l'image
        x = image_centre_um_x - (taille_img_x_pix/2)*taille_pix_x_um
        y = image_centre_um_y - (taille_img_y_pix/2)*taille_pix_y_um
        
        self.meta_img.insert(0,x)
        self.meta_img.insert(1,y)

         
    def pix_to_um(self,cover_s):
        
        """
        Je transforme les données en pix pour correspondre avec mon image (à tester en réel parce que j'ai un gros décalage avec la simulation)
        """
        cvr_s = np.zeros((len(cover_s),len(cover_s[0])))
                        
        for i in range(0,len(cover_s)):
            for j in range(0,len(cover_s[i])):
                
                if j == 3 or j == 2 :
                    cvr_s[i][j]=int(cover_s[i][j] * self.meta_img[j]*2)

                else :
                    cvr_s[i][j]=int(cover_s[i][j] * self.meta_img[3]+ self.meta_img[j])
        
        return cvr_s
    
    def create_cvs_coverslip(self):
        
        """
        Creer un .cvs dans data en fonction de la position de la lamelle dans le container dans le microscope
        """
        
        self.pick_some_metadata()
        cvr_s = self.pix_to_um(self.cood.coverslips)

        fichier = open('.\\\data\'+"data_coverslips.txt", "w")

        for i in range(0,len(cvr_s)):
            for j in range(0,len(cvr_s[i])):    
                fichier.write(str(int(cvr_s[i][j]))+" ")
            fichier.write('\n')
            
        fichier.close()
        
    def create_cvs_container(self):
        
        """
        Creer un .cvs dans data en fonction de la position de la lame dans le container dans le microscope
        """
        
        self.pick_some_metadata()
        cvr = self.pix_to_um(self.cood.containers)

        fichier = open('.\\data\'+"data_containers.txt", "w")

        for i in range(0,len(cvr)):
            for j in range(0,len(cvr[i])):    
                fichier.write(str(int(cvr[i][j]))+" ")
            fichier.write('\n')
            
        fichier.close()
     




