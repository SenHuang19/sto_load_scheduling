import pandas as pd
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import datetime
import matplotlib.pyplot as plt
import csv

baseline = pd.read_csv('baseline.csv')[:1440*30]

rtp = pd.read_csv('rtp.csv')[:1440*30]

control_det = pd.read_csv('det.csv')

control_sto = pd.read_csv('sto.csv')

price = pd.read_csv('price.csv')


meas_data_det = pd.read_csv('measurement_power_det.csv')[1:]

meas_data_sto = pd.read_csv('measurement_power_sto.csv')[1:]

powerpoints = ['PSZ-1 SOUTH F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-2 EAST F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-3 NORTH F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-4 WEST F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-5 CORE F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-6 SOUTH F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-7 EAST F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-8 NORTH F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-9 WEST F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-10 CORE F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)']

baseline['power'] = [0]*len(baseline)

control_det['power'] = [0]*len(control_det)

control_sto['power'] = [0]*len(control_sto)

rtp['power'] = [0]*len(rtp)

meas_data_det['target'] = [0]*len(meas_data_det)

meas_data_sto['target'] = [0]*len(meas_data_sto)

for i in range(10):
     meas_data_det['target'] = meas_data_det['target'] + meas_data_det['HP{}Target'.format(i)]
     meas_data_sto['target'] = meas_data_sto['target'] + meas_data_sto['HP{}Target'.format(i)]
for powerpoint in powerpoints:

    baseline['power'] = baseline['power'] + baseline[powerpoint]/1000.
    
    control_det['power'] = control_det['power'] + control_det[powerpoint]/1000.

    control_sto['power'] = control_sto['power'] + control_sto[powerpoint]/1000.

    rtp['power'] = rtp['power'] + rtp[powerpoint]/1000.
sum11=0
sum22=0
sum221=0
sum33=0
for i in range(15):

   baseline_sec = baseline['power'][i*1440:(i+1)*1440].tolist()
   
   meas_data_det_sec = meas_data_det['target'][i*1440:(i+1)*1440].tolist()
   control_det_sec = control_det['power'][i*1440:(i+1)*1440].tolist()

   meas_data_sto_sec = meas_data_sto['target'][i*1440:(i+1)*1440].tolist()
   control_sto_sec = control_sto['power'][i*1440:(i+1)*1440].tolist()   
   
   rtp_sec = rtp['power'][i*1440:(i+1)*1440].tolist()
#   print(len(rtp_sec))
   sum1 = 0
   sum2 = 0
   sum21 = 0
   sum3 = 0
   for s in range(len(baseline_sec)):
       sum1=sum1+ baseline_sec[s]*price['price'].iloc[s]
       sum2=sum2+ control_det_sec[s]*price['price'].iloc[s] 
       sum21=sum21+ control_sto_sec[s]*price['price'].iloc[s] 
       sum3=sum3+ rtp_sec[s]*price['price'].iloc[s]
       meas_data_det_sec[s] = meas_data_det_sec[s]/1000.
       meas_data_sto_sec[s] = meas_data_sto_sec[s]/1000.
   sum11=sum11+ sum1   
   sum22=sum22+ sum2
   sum221=sum221+ sum21   
   sum33=sum33+ sum3
  
   fig, (ax1,ax2,ax3,ax4) = plt.subplots(4, sharex=True)
   
   x = pd.date_range(start='8/1/2017 00:00:00', end='8/2/2017 00:00:00',freq='1min')[:-1]
   
   dates =  matplotlib.dates.date2num(x)
   
   tab = pd.DataFrame()
   
   tab['baseline'] = baseline_sec

   tab['control'] = control_det_sec   

   tab['control_opt'] = control_sto_sec   

   tab['rtp'] = rtp_sec
   
   if sum1 >0:

      ax1.plot_date(dates,tab['baseline'].rolling(window=30).mean(),linestyle='-',label='baseline',marker='')
      ax1.plot_date(dates,tab['rtp'].rolling(window=30).mean(),linestyle='-',label='rtp:{}%'.format(round(100-(sum3/sum1)*100)),marker='')
      ax2.plot_date(dates,tab['control'].rolling(window=30).mean(),linestyle='-',label='det:{}%'.format(round(100-(sum2/sum1)*100)),marker='')
      ax3.plot_date(dates,tab['control_opt'].rolling(window=30).mean(),linestyle='-',label='det:{}%'.format(round(100-(sum21/sum1)*100)),marker='')
      ax2.legend(loc='best')
      ax3.legend(loc='best') 

      ax2.plot_date(dates,meas_data_det_sec,linestyle='-.',label='target',marker='')
      ax3.plot_date(dates,meas_data_sto_sec,linestyle='-.',label='target',marker='')
 
      ax4.plot_date(dates,price['price'],linestyle='-',label='control',marker='')
      myFmt = mdates.DateFormatter('%H:%M')
      ax4.xaxis.set_major_formatter(myFmt)
      ax1.legend(loc='best')
     
      plt.savefig('case_{}.png'.format(i))
   
# print(round(100-(sum22/sum11)*100))
# print(round(100-(sum22/sum33)*100))
