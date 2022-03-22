import socket
import time as tm
import numpy as np
import sys
import random as rd
import json,collections
import os
import random as rd
from numpy import array
from shutil import copyfile
import pandas as pd
import requests
import csv


def PID(Kp, Ki, SP, MEA, e_pre):
    # initialize stored data
    if SP<0.1 and MEA <0.1:
       e = 0
    else:
       e = (SP - MEA)/max(SP,MEA)

    
        
    P = Kp*e
        
    I = Ki*(e+e_pre)
        
    return P+I, e+e_pre

class socket_server:

    def __init__(self):     
          self.sock=socket.socket()
          self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          host=socket.gethostname()
          port=12345
          self.sock.bind(("127.0.0.1",port))
          self.sock.listen(10)
		  
def data_parse(data): 
    data=data.replace('[','')     
    data=data.replace(']','')  	
    data=data.split(',')

    for i in range(len(data)):
	              data[i]=float(data[i])
         
    return data

def read_data(file_name): 
    reg=np.loadtxt(file_name)
    reg_ref=[abs(number) for number in reg]
    reg=reg/max(reg_ref)
    return reg

	
def EP(model_path,startmonth,startday,endmonth,endday,timestep):

        f = open(model_path, 'r')
        lines = f.readlines()
        f.close()
		
        for i in range(len(lines)):
            if lines[i].lower().find('runperiod,') != -1:
                lines[i + 2] = '    ' + str(startmonth) + ',                       !- Begin Month' + '\n'
                lines[i + 3] = '    ' + str(startday) + ',                       !- Begin Day of Month' + '\n'
                lines[i + 4] = '    ' + str(endmonth) + ',                      !- End Month' + '\n'
                lines[i + 5] = '    ' + str(endday) + ',                      !- End Day of Month' + '\n'
                lines[i + 6] = '    Monday,                  !- Day of Week for Start Day' + '\n'
            elif lines[i].lower().find('timestep,') != -1 and lines[i].lower().find('update frequency') == -1:
                if lines[i].lower().find(';') != -1:
                    lines[i] = '  Timestep,' + str(timestep) + ';' + '\n'
                else:
                    lines[i + 1] = '  ' + str(timestep) + ';' + '\n'                    
        f = open(model_path, 'w')
        for i in range(len(lines)):
            f.writelines(lines[i])
        f.close()	
	

def write_port_file(port,host):
        fh = open('socket.cfg', "w+")
        fh.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        fh.write('<BCVTB-client>\n')
        fh.write('  <ipc>\n')
        fh.write('    <socket port="%r" hostname="%s"/>\n' % (port, host))
        fh.write('  </ipc>\n')
        fh.write('</BCVTB-client>')
        fh.close()


	

def writeVariableFile(config):
    default=[]
    with open(config) as f:
        config=json.load(f,object_pairs_hook=collections.OrderedDict)
        if 'inputs' in config: 
            INPUTS = config['inputs']
#        print INPUTS
        if 'outputs' in config:
            OUTPUTS = config['outputs']
#        print(OUTPUTS)
        ePlusOutputs=0
        ePlusInputs=0
        fh = open('variables.cfg', "w+")
        fh.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        fh.write('<!DOCTYPE BCVTB-variables SYSTEM "variables.dtd">\n')
        fh.write('<BCVTB-variables>\n')
#        for obj in OUTPUTS.itervalues():
        for obj in OUTPUTS.keys():
             obj = OUTPUTS[obj]
#             print(type(obj))
#            if obj.has_key('name') and obj.has_key('type'):
             if 'name' in obj and 'type' in obj:
                ePlusOutputs = ePlusOutputs + 1
                fh.write('  <variable source="EnergyPlus">\n')
                fh.write('    <EnergyPlus name="%s" type="%s"/>\n' % (obj.get('name'), obj.get('type')))
                fh.write('  </variable>\n')
#        for obj in INPUTS.itervalues():
        for obj in INPUTS.keys():
             obj = INPUTS[obj]
#             print(type(obj))
#            if obj.has_key('name') and obj.has_key('type'):
             if 'name' in obj and 'type' in obj:
                ePlusInputs = ePlusInputs + 1
                fh.write('  <variable source="Ptolemy">\n')
                fh.write('    <EnergyPlus %s="%s"/>\n' % (obj.get('type'), obj.get('name')))
                fh.write('  </variable>\n')
                default.append(obj.get('default'))
        fh.write('</BCVTB-variables>\n')
        fh.close()
        return ePlusInputs, default


def work(url):
	''' Run the model in its directory. '''
	# Delete output file every run if it exists
#	u={}
	with open('./input.json') as f:
         data = f.read()
	u = json.loads(data)
#	json_object = json.dumps(u, indent = 4,default=str)
	result = requests.post('{0}/calculate'.format(url), json=u).json()
	# with open('./output.json','w') as f:
	# 	json.dump(result, f)
	# print result
	return result

server=socket_server()
Ndays = 30 # number of days for simulation
Nmins = Ndays*1440
# Starting from August 1
EP(sys.argv[1],8,1,8,Ndays,60)
ePlusInputs,default=writeVariableFile(sys.argv[2])
#print default
write_port_file(12345,'127.0.0.1')

vers = 2
flag = 0

# dev=float(sys.argv[3])

# start=float(sys.argv[4
          
#server.sock.listen(10)

conn,addr=server.sock.accept()
index=0
index1 = 0
power = []
e_sum = []
# Psp_df = pd.read_csv('real_power_pred.csv')
Toa_df = pd.read_csv('data_record/August_daily_oat.csv')['OutdoorAirTemperature']
Tsp_df = pd.read_csv('data_record/August_daily_setpoint.csv')['ZoneCoolingTemperatureSetpoint']
Toa_hourly = Toa_df.groupby(np.arange(len(Toa_df))//60).mean()
Tsp_hourly = Tsp_df.groupby(np.arange(len(Tsp_df))//60).mean()

# print(Psp)
length = 30
# Psp = []
Meas = []
Targets = []
for z in range(10):
    temp = []
    temp2 = []
    for t in range(Nmins+10):
        temp.append(0)
        temp2.append(0)
    Meas.append(temp)
    Targets.append(temp2)
    e_sum.append(0)
    power.append([])
temps = []
#print(len(Meas[0])) 
Ptarget = []
for z in range(10):
    Ptarget.append(1000)

while 1:

### data received from eplus
         
         data = conn.recv(10240)
		 
#         print('I just got a connection from ', addr)
#         print data
         data = data.rstrip()

         arry = data.split() 
#         print arry
         flagt = float(arry[1])
         if flagt==1:
                 conn.close()
                 # directory='result2/'+sys.argv[5]+'/'+sys.argv[1].split('_')[1]
                 # print directory
                 tm.sleep(5)
                 # save Psp
                #  Psp_df = pd.DataFrame()
                #  for z in range(10):
                #     Psp_df['HP'+str(z)] = Psp[:][z]
                #     # print(Psp[:][z])
                 table = pd.DataFrame()
                 for z in range(10):
                     table['HP'+str(z)+'Measurement'] = Meas[z]
                     table['HP'+str(z)+'Target'] = Targets[z]                     
                 table.to_csv('measurement_power.csv')

                 # if not os.path.exists(directory):
                                 # os.makedirs(directory)
                 # copyfile('output/'+sys.argv[1]+'.csv', directory+'/'+str(start)+'_'+str(dev)+'.csv')
                 # copyfile('output/'+sys.argv[1]+'.eio', directory+'/'+str(start)+'_'+str(dev)+'.eio')
                 # copyfile('output/'+sys.argv[1]+'.eso', directory+'/'+str(start)+'_'+str(dev)+'.eso')
                 # copyfile('output/'+sys.argv[1]+'Table.html', directory+'/'+str(start)+'_'+str(dev)+'.html')
                 # copyfile('output/'+sys.argv[1]+'.idf', directory+'/'+str(start)+'_'+str(dev)+'.idf')								 
                 sys.exit()
         if len(arry)>=6:
#              print(arry)
              time=float(arry[5]) # time step in seconds starting from 0
#              print(time)
              temp2 = []
              for i in range(10):
                  temp2.append(float(arry[26+i]))
              temps.append(temp2)
              if (index == 0) | (index%60 == 59):
#                  print(len(temps))
                  if len(temps)>=60:
                      Ptarget = []
                      t = int(time//60)
                      t_h = int(time//3600)
                      hrz1 = [tt for tt in range(t_h+1,t_h+25,1)]
                      hrz2 = hrz1
                    #   hrz2 = [tt%(24*7) for tt in range(t_h+1,t_h+25,1)]
                    #   print(hrz1)
                      print('Time in minute: '+str(t))
#                      print('ZoneTemp1 in C:'+str([row[0] for row in temps]))
#                      print('Oat in C: '+str([Toa_hourly.iloc[i] for i in hrz1]))
                      input_dict = {
		                        "OutdoorAirTemperature" : Toa_hourly.iloc[t_h],
		                        "Time"    : time,
                                "forecast": [Toa_hourly.iloc[i] for i in hrz1],
                                "Tzon1"   : [row[0] for row in temps],
                                "Tzon2"   : [row[1] for row in temps],
                                "Tzon3"   : [row[2] for row in temps],
                                "Tzon4"   : [row[3] for row in temps],
                                "Tzon5"   : [row[4] for row in temps],
                                "Tzon6"   : [row[5] for row in temps],
                                "Tzon7"   : [row[6] for row in temps],
                                "Tzon8"   : [row[7] for row in temps],
                                "Tzon9"   : [row[8] for row in temps],
                                "Tzon10"  : [row[9] for row in temps],
                                "Trzon1"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon2"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon3"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon4"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon5"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon6"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon7"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon8"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon9"  : [Tsp_hourly.iloc[i] for i in hrz2],
                                "Trzon10" : [Tsp_hourly.iloc[i] for i in hrz2]}

                      with open('./input.json','w') as f:
                          json.dump(input_dict, f)
                        # print(input_dict["Trzon2"])
                      result = work('http://127.0.0.1:5000')
                      for z in range(10):
                        Ptarget.append(result['HP'+str(z+1)])
                      temps = []
              output = []
              print(index)              
              for z in range(10):
                power[z].append(float(arry[z+66])) # 66 - HP1, 74 - HP10
                if len(power[z])>length:
                    power[z].pop(0)                                      
                    Meas[z].append(sum(power[z])/float(length))
                    Targets[z].append(Ptarget[z])
#                print(len(power[z]))
                # print(Meas[z][index])
                # print(Ptarget[z])
                if index%1440==0:
                    temp1, e_sum[z] = PID(10,1/6000.,Ptarget[z],Meas[z][index],0)                 
                else:     
                    temp1, e_sum[z] = PID(10,1/6000.,Ptarget[z],Meas[z][index],e_sum[z]) # P, I, Setpoint, measurement, err accumulation
                output.append(temp1)
#              print(output)
              
#              print(TS)
#              print(float(arry[69]))
              mssg = '%r %r %r 0 0 %r' % (vers, flag, ePlusInputs, time) 
              for z in range(10):  
                TS = float(arry[-1-(9-z)])
                mssg=mssg+' '+str(TS-min(max(output[z],-2),2)) # loop for 9 more zones
#              print(mssg)              
              for i in range(10,ePlusInputs): # 1,2 ...
			  			  # if index>=start*60 and index<start*60+30:
			                              mssg=mssg+' '+str(float(arry[-1-i]))                                      
						  # # else:
			                              # mssg=mssg+' '+str(default[i])						  
              # if index>=start*60 and index<start*60+30:
                           # print mssg
              conn.send((mssg+'\n').encode())
         index=index+1


