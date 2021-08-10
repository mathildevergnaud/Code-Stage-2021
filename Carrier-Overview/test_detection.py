# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 10:33:36 2021

@author: User
"""
from CarrierOverview import CarrierOverview as co
from ContainerCoverslipDetector import ContainerCoverslipDetector as cc
from CoordonneeCoverslip import CoordonneeCoverslip as Coc
                    
                   
input_dir = './datasets/'
filename = 'CarrierOverview.czi'


co_obj = co(input_dir, filename)
cc_obj = cc(co_obj)

cc_obj.find_circular_coverslips_in_containers()
cc_obj.show("Je suis laaaa")

aivia = Coc(cc_obj,co_obj)

aivia.create_cvs_coverslip()
aivia.create_cvs_container()
