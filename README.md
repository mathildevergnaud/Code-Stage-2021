# Code-Stage-2021
Automatisation d'un microscope de Zeiss le Cell Discover 7

__Carrier Overview :__

Ce fichier contient les classes qui permettent de détecter la lamelle dans un container, de transmettre les coordonées du centre de la lamelle et du container dans un dossier data.
C'est ce dossier data que la macro réalisée sous Zeiss va lire et récupérer ces informations.

__Detection Canny :__

Première méthode pour détecter les coupes, en réhaussant le contour des coupes par un filter de Canny. 

__Detection Shen Castan :__ 

Seconde méthode pour détecter les coupes, en réhaussant le contour des coupes avec un filtre de Shen Castan modifié.

__Détection des coupes par Deep-learning :__

La dernière méthode pour détecter les coupes est par Deep-learning avec le réseau de neuronne Pix2Pix de Google Colab.
On le modifie pour l'adapter à nos images.

__Macro Zeiss :__

Macro réalisé pour lancer une acquisition d'un microscope Zeiss sous Zen. 
