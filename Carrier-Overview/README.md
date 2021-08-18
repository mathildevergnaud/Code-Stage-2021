Ces classes dépendent de deux librairies :

	-OpenCV Python - pip install opencv-python - permet d'effectuer du traitement d'image
	-czifile - pip install czifile - ouvrir les images au format .czi

__CarrierOverview__ 

Ouvre l'image et les métadatas
A partir des métadatas, il détermine le centre de l'image en mm suivant le repère platine  

__ContainerCoverslipDetector__

Cette classe dépend de la classe CarrierOverview
elle permet d'identifier les coordonnées et le centre des containers et des lamelles

__CoordonneeCoverslip__

Dépedend des deux précédentes classes,
Cette classe convertit les données acquises grâce à la classe ContainerCoverslipDetector en repère platine. 


