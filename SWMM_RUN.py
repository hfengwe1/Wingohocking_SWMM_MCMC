## SWMM runs, read the inp, run and collect the results
import os
#import numpy as np
#from pandas import DataFrame
import random as rd

#import s_objects
#from s_read import read_inp
from mc_read_inp import read_report
from mc_read_inp import read_inp
from datetime import datetime
from swmm5.swmm5tools import SWMM5Simulation

os.chdir('C:\\School\\3rd paper - case study\\90. SWMM simulation\\BW_2018')

##Run SWMM model with runParamlist (the modified parameter set), swmmInpFile  
##(the tempelate inp file), treament rate(cap_r), GI infiltration rate (ksat_r)
def runswmm(model1, lidname,runParamList,swmmInpFile,simulation_date,sub_i):
# read inp file and change Lid's ksat value

# Write out the model to a new file because SWMM must have a file
    Catchment = ['UrbanLand','UrbanComplex','Manor']
    subcat = Catchment[sub_i]
    f = open('SWMM_modified.inp','w')
    swmmInputFileStr=model1.output()
    f.write(swmmInputFileStr)  # write out the swmmInputFileStr for modified problem
    f.close()
 
# show the Impervious Treated Percentage of GI in subwatersheds
    imperv_i=[0,0,0]
    imperv_i[0] = swmmInputFileStr.find('UrbanLand\t'+lidname+'\t')
    imperv_i[1] = swmmInputFileStr.index('UrbanComplex\t'+lidname+'\t')  
    imperv_i[2] = swmmInputFileStr.index('Manor\t'+lidname+'\t')
    imperv_treated=[0,0,0]
    for i in range(0,3):
        lineList = swmmInputFileStr[imperv_i[i]:].split('\n',1)   ## lists of lines from .inp, split by '\n'
        wordList = lineList[0].split()      
        imperv_treated[i]=wordList[6]
#    print('impervious treated = ', imperv_treated)
   
    # Run the new model file
    startTime = datetime.now()   # obtain the starting time of the run
#    startTimeStr = str(startTime)
    st=SWMM5Simulation("SWMM_modified.inp","SWMM_modified.txt")
    
    endTime = datetime.now()   # obtain the ending time of the run
    elapsedTime = endTime - startTime
    minAndSec = divmod(elapsedTime.total_seconds(), 60)
    elapsedTimeStr = "%s min, %0.2f sec" % minAndSec
    area = runParamList[sub_i]['Area']
    N_GI = runParamList[sub_i]['Number']
    print(elapsedTimeStr)
    (peak,volume,lidDict) = read_report("SWMM_modified.txt")
    if lidname =="RainBarrel" and N_GI>0:
        vol_in = (float(lidDict[subcat+' '+lidname]['Total Inflow'])-
                  float(lidDict[subcat+' '+lidname]['Surface Outflow'])) 

        vol_re_MG = vol_in/12.0*area*N_GI*7.48/1000000  # runoff reduction
        volume = volume - vol_re_MG
        
    run = { "peak": peak, "volume": volume, "lidDict": lidDict, 
            "runParamList": runParamList, "imperv_treated": imperv_treated}
    return (run)

