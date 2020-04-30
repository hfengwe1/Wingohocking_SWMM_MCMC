# -*- coding: utf-8 -*-
"""
Created on Thu May 24 05:59:27 2018

@author: Fengwei
"""
import os
os.chdir('C:\\School\\3rd paper - case study\\90. SWMM simulation\\BW_2018')
import random as rd
import numpy as np
import pandas as pd
#from pandas import DataFrame
from s_objects import *
#from s_read import read_inp
#from s_read import read_report
from mc_read_inp import read_inp
#from Storage_read import read_report_s

from datetime import datetime
#from SWMM_DR_K import runswmm
from SWMM_RUN import runswmm
import yaml
#from swmm5.swmm5tools import SWMM5Simulation

#%% File Names
# the file names and basic settings

swmmInpFile = 'SWMM_BW2018_new.inp'  
#swmmInpFile = 'Big_Wingohocking0719.inp'  
yamlFile='Wingo_sub_list_RG.yaml'
Ksat_new=[0.1,0.1,0.1] #background Ksat
dateTime = datetime.now()
n_sub = 3  # number of subcatchments
N=15 # number of GI Installation
n_runs = 1   # number of MC simulation runs
lidname='RG'

dateTime = datetime.now()
DtoG=23      # dr = treated area/GI area, e.g. capRatioPct =5 means 
           # the area treated is 5 times as large as the GI area
#year = [2001]
#start_date='01/01/str(year[0])
#end_date='12/31/' +str(year[0])
#simulation_date=[start_date,end_date]
# values of the parameters
Seepage_new = 0.4 # background Ksat (in/hr)
BermH = 6  # berm hight (in)
Catchment = ['UrbanLand','UrbanComplex','Manor']
#%%  Read swww.inp and modify it to create new input file (SWMM_modified.inp)    
#  Baseline Scenario - no GI   
"""
  ##	types = ['BC','RG','GR','IT','PP','RB','RD','VS']
	layers = ['SURFACE','SOIL','PAVEMENT','STORAGE','DRAIN','DRAINMAT']
	# pdict is a dictionary keyed by the LID layer
	layer/param = { SURFACE':['StorHt','VegFrac','Rough','Slope','XSlope'],
                    Soil: [Thick','Por','FC','WP','Ksat','Kcoeff','Suct'],
                    STORAGE: ['Thick','Vratio','FracImp','Perm','Vclog'],
                            :['Height','Vratio','Seepage','Vclog'],
                            'Coeff','Expon','Offset','Delay'],
        			   DRAINMAT':['Thick','Vratio','Rough']}
"""    

#%% MC Simulation 
Years = range(1980,2013)
#Years = [2001]

#for j in range(n_sub): # for each catchment:
for j in [0,1,2]: # for each catchment:
    P_GI_ac = []
    YEAR=[]
    TreatedArea=[]
    vol_N = []
    BermHeight = []
    Seepage_r = []      
    sub_i=j 
    for year in Years:
  
        
        start_date='01/01/'+str(year)
        end_date='12/31/' +str(year)
        simulation_date=[start_date,end_date]
        # Create an instance of a swmm_model object using the SWMM inp data:
        (section_names,sections) = read_inp(swmmInpFile,simulation_date)
        model1 = swmm_model('Model1',section_names,sections)
        
        f = open(yamlFile,'r')
        runParamList = yaml.load(f)   # runParam has the values of the variables - installation of GI etc
        f.close()  
        
        # read data from YAML file - GI Usage
        for item in runParamList:  ## reset the model
            subcat = item['Subcat']    #name of the subcatchment
            lid = item['LID']          #lid type
            newnumber = item['Number'] #number of lid installation
            newarea = item['Area']     #subcatchment area
            DtoG = item['DrainageToGI']    # treated area/total area
            model1.lidChangeNumber(subcat,lid,newnumber)  # change PercImperv
            model1.lidChangeArea(subcat,lid,newarea,DtoG)   # impervious treated by GI     
        run = runswmm(model1, lidname,runParamList,swmmInpFile,simulation_date,sub_i)
        peak0 = float(run.get('peak'))   # peak discharge w/o GI 
        volume0 = float(run.get('volume'))
        peak_0 = peak0*np.ones(n_runs)
        vol_0 = volume0*np.ones(n_runs)
       
        imperv_ur=[]
        imperv_cx=[]
        imperv_ma=[]
        peak_re = []
        vol_re = []
        vol_1 = []    
        DR=[]
  
        for run in range(n_runs): # MC simulation 
#########################################################################    
            DtoG = rd.gauss(23,4)  # generate random number from Norm(mu,std) for treated areau
            if DtoG<2:
                DtoG = 2
            BermH = 1+2*rd.random()  # change the storage 
            Seepage_new= rd.gauss(0.4,0.12)
            if Seepage_new <0.05:
                Seepage_new = 0.05
#########################################################################    

            GI_area = 43560.0
            DR.append(DtoG)
            model1.lidControl(lidname,'SURFACE','StorHt', BermH)  # change Berm Height
            model1.lidControl(lidname,'STORAGE','Seepage', Seepage_new)    
            ## Change Seepage rate in GI - RainGarden - Storage layer      
            model1.lidChangeNumber(Catchment[sub_i],lidname,N)  # change PercImperv
            model1.lidChangeArea(Catchment[sub_i],lidname,GI_area,DtoG)   # impervious treated by GI 
        
            run = runswmm(model1, lidname,runParamList,swmmInpFile,simulation_date,sub_i)
            peak1= round((float(peak0)-float(run.get('peak'))),2)  # peak discharge reduction
            peak_re.append(peak1)  # list of peak discharge
            volume1=run.get('volume')
            vol_1.append(volume1)
            vol_N.append(volume0)
            rf_r=round(volume0-volume1,2)
            vol_re.append(rf_r)
            imperv_treated=run.get('imperv_treated')  
            imperv_ur.append(imperv_treated[0])
            imperv_cx.append(imperv_treated[1])
            imperv_ma.append(imperv_treated[2])   
    #      print("The Drainage-to-GI Area Ratio is %s  ", dr)
            print "The treated area is %s ac " %round(DtoG*N,1)
            P_GI_ac.append(rf_r/N)
            YEAR.append(year)
            TreatedArea.append(DtoG*N)
            BermHeight.append(BermH)
            Seepage_r.append(Seepage_new)
            
            
    #    runParamList[sub_i]['Number']= 0  # number of GI units
        model1.lidChangeNumber(Catchment[sub_i],lidname,0)  # change the GI installation to 0
        model1.lidChangeArea(Catchment[sub_i],lidname,GI_area,DtoG)   # impervious treated by GI 
    
        print "The annual runoff is: %s MG " %vol_1  
        df = pd.DataFrame({'Runoff_noGI': vol_0,'Runoff_w_GI':vol_1, 'Runoff_Reduction': vol_re,
                  'drain_to_GI_r': DR,'imperv_urban':imperv_ur,
                  'imperv_complex':imperv_cx,'imperv_manor':imperv_ma,'Berm_Height':BermH})
        fresult=str(year)+Catchment[sub_i]+lidname+'.xlsx'
        df.to_excel(fresult, sheet_name='sheet1', index=False)

    df2 = pd.DataFrame({'GI_reduction(MG/ac)':P_GI_ac,'Year':YEAR, 'Treated Area(ac)': TreatedArea,'Berm_Height(in)':BermHeight,'Seepage(in/hr)':Seepage_r,'Runoff_noGI': vol_N})
    result_all='GI_Reduction_ac'+Catchment[sub_i]+lidname+'.xlsx'
    df2.to_excel(result_all, sheet_name='sheet1', index=False)