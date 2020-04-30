# -*- coding: utf-8 -*-
"""
swmmread.py
it's read and write 
Read SWMM input file and create objects for each input category
Also read the resulting output file after SWMM is runcp

Fengwei
 - update GI control - bern hight (storage) 
 Generate an input file: SWMM_modified.inp 
"""
#import random as rd

def read_inp(swmmInpFile,simulation_date):
# read SWMM inp file fname into a large string
    infile = open(swmmInpFile,'r')
    swmmInpStr = infile.read()
    infile.close()
    data = swmmInpStr
    section_names = []   

    start_i = data.find('START_DATE')
    if start_i >= 0:  # The lid control line is found
#change Start Date
     lineList = data[start_i:].split('\n',5)   ## lists of lines from .inp, split by '\n'
     wordList = lineList[0].split()           ## lists of words from the first line(list) in lineList split by ' '
     lineList_i=str(lineList[0])
     lineList_i=lineList_i.replace(wordList[1],str(simulation_date[0]))
     data=data.replace(str(lineList[0]), lineList_i)   
#change Report Start Date
     wordList = lineList[2].split()           ## lists of words from the first line(list) in lineList split by ' '
     lineList_i=str(lineList[2])
     lineList_i=lineList_i.replace(wordList[1],str(simulation_date[0]))
     data=data.replace(str(lineList[2]), lineList_i)      
#change End Date
     wordList = lineList[4].split()           ## lists of words from the first line(list) in lineList split by ' '
     lineList_i=str(lineList[4])
     lineList_i=lineList_i.replace(wordList[1],str(simulation_date[1]))
     data=data.replace(str(lineList[4]), lineList_i)      
# Write out the model to a new file because SWMM must have a file
     f = open("SWMM_modified.inp",'w')
     swmmrandinp=data
     f.write(swmmrandinp)  # write out the swmmInputFileStr for modified problem
     f.close()
####          
# remove comment lines and blank lines and identify all section names used in the file
    infile = open('SWMM_modified.inp','r')
    swmmInpLine = infile.readlines()
    infile.close()
    data1 = []
    for line in swmmInpLine:
        line_ns = line.strip()  # remove whitespace
        if line_ns.startswith('['):
            section_names.append(line_ns)
        elif line_ns.startswith(';;'):  # do not include comment ines
           continue
        elif not line_ns:  # do not include blank lines
           continue
        data1.append(line)  # data1 is a list containing the unstripped lines of the SWMM .inp file 
# now find all data lines in each section, store each data line as an entry in a 
# then after reading all the data in a section, store the section_list in
# dictionary sections keyed by the section name
    sections = {}  # dictionary to hold all lines in a section, keyed by section_names
    end = False
    for i in range(len(data1)):
        line = data1[i]
        line_ns = line.strip()  # remove whitespace
        if line_ns in section_names:
            name = line_ns
            section_list = []
            try:
               next_line = data1[i+1]  # look ahead at next line
            except IndexError:
               end = True         # end of input file found
            next_line_ns = next_line.strip()  # remove whitespace
            if (end or (next_line_ns in section_names)):  # we have read the entire section
              sections[name] = section_list              # store the list in the dictionary
        else:
           section_list.append(line)    # store section data in section_list
           try:
               next_line = data1[i+1]  # look ahead at next line
           except IndexError:
               end = True
           next_line_ns = next_line.strip()  # remove whitespace
           if (end or (next_line_ns in section_names)):
              sections[name] = section_list  #populate the sections dictionary
    return((section_names,sections))  # return the section_names LIST and the sections DICTIONARY (keyed by items in the section_names list)

def read_report(fname,):
  infile = open(fname,'r')
  data = infile.read()
  # find and parse the External Outflow line
  external_flow_index = data.find('External Outflow')
  if external_flow_index >= 0:  # The External Outflow line is found
    lineList = data[external_flow_index:].split('\n',1)
    wordlist = lineList[0].split()
    volume = float(wordlist[4])
  else:
    volume = None
   
  lid_ps_index =data.find('LID Performance Summary\n')
  Barrel_index=data.find('RainBarrel')
  
#  if Barrel_index >= 0:  # The External Outflow line is found
#    lineList = data[lid_ps_index:].split('\n') # split the lines
#    wordlist = lineList[8].split()   # find lid performance 
#
#    lineList_b = data[Barrel_index:].split('\n',1) # split the lines
#    wordlist_b = lineList_b[0].split()   # find lid performance 
#    Runoff_reduction=((float(wordlist_b[1])-float(wordlist_b[4]))/12*7.4805/1000000)
#    # 1 ft^3 = 7.4805 gallon
#    volume = volume-Runoff_reduction
#  else:
#    volume = volume

  # find peak flow (CFS)
  peak_index=data.find('Subcatchment Runoff Summary')
  if peak_index >=0: # the subcatchment runoff summary section in the output file
    peak_head_index= data.find('Subcatchment', peak_index)
    peak_lines=data[peak_head_index:].split('\n')
    pline=peak_lines[8]
    runoff_dict = {}
    sub_dict = {}
#    for line in peak:
    this_runoff_dict={}
    labels = ['Subcatchment', 'Total Precip','Total Runon','Total Evap','Total Infil', 
              'Total Runoff(in)', 'Total Runoff', 'Peak(CFS)', 'Runoff Coeff']
    wordlist_1 = pline.split()   
    sub = wordlist_1[0]  # string containing subcatchment name  
    values = wordlist_1[1:]         
    peak_v = wordlist_1[7]
        
#        i = 0;
#      for label in labels:
#        runoff_dict[label] = float(values[i])
#        i += 1
#        runoff_dict[sub] = this_runoff_dict  # to be stored in mongo database
#        peak_v=   
           
  else:
    peak_v = None          
           
       # find and parse the LID Performance Summary
  lid_start_index = data.find('LID Performance Summary')
  if lid_start_index >= 0:   # The LID Performance Summary section is in the output file
    lid_subcatchment_heading_index = data.find('Subcatchment',lid_start_index)
    remaining_lines = data[lid_subcatchment_heading_index:].split('\n') 
    #line_after_section = '  '
    i = 2
    lid_performance = []
    while True:
      if remaining_lines[i].strip() == '':   # Blank line found
        break
      lid_performance.append(remaining_lines[i])
      i = i + 1
    lid_dict = {}
    series_dict = {}
    for line in lid_performance:
      this_lid_dict = {}
      labels = ['Total Inflow', 'Evap Loss', 'Infil Loss', 'Surface Outflow', 'Drain Outflow', 
                'Initial Storage', 'Final Storage', 'Continuity Error']
      wordlist = line.split()   
      idx = wordlist[0] + ' ' + wordlist[1]   # string containing subcatchment name and lid name
      values = wordlist[2:]
      i = 0;
      for label in labels:
        this_lid_dict[label] = float(values[i])
        i += 1
      lid_dict[idx] = this_lid_dict  # to be stored in mongo database
      # construct a Pandas dataframe:
      # series_dict[idx] = pd.Series(values, index = labels) 
      # lid_report = pd.DataFrame(series_dict)
      infil_loss = this_lid_dict['Infil Loss']
  else:
    lid_dict = None
    lid_report = None
    infil_loss = None
  # find and parse the Outfall Loading Summary    
  #outfall_start_index = data.find('Outfall Loading Summary')
  #output_start_index = data.find('System',outfall_start_index)
  #split = data[output_start_index:].split('\n',1)
  #output_line = split[0]
  #output_list = output_line.split()
  #infil_loss = float(output_list[3])
  #volume = float(output_list[4])
  
  return (peak_v,volume,lid_dict)
  # infil_loss and volume are strings.  lid_dict is a dictionary of dicts


