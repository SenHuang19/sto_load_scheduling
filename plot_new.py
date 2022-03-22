import pandas as pd
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import datetime
import matplotlib.pyplot as plt
import csv

case = 'Case1 - length=30'

baseline = pd.read_csv('baseline.csv')[:1440*30]

rtp = pd.read_csv('rtp.csv')[:1440*30]

#control = pd.read_csv(case+'/Others/eplusout.csv')

#price = pd.read_csv(case+'/saved/sol_T1440.csv')[1:]

#price = price.loc[price.index.repeat(60)].reset_index(drop=True)

price = pd.read_csv('price.csv')


#meas_data = pd.read_csv(case+'/Others/measurement_power.csv')[1:]

powerpoints = ['PSZ-1 SOUTH F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-2 EAST F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-3 NORTH F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-4 WEST F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-5 CORE F2 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-6 SOUTH F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-7 EAST F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-8 NORTH F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-9 WEST F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)', 'PSZ-10 CORE F1 COOLING COIL:Cooling Coil Electric Power [W](TimeStep)']

baseline['power'] = [0]*len(baseline)

#control['power'] = [0]*len(control)

rtp['power'] = [0]*len(rtp)

#meas_data['target'] = [0]*len(meas_data)

# for i in range(10):
     # meas_data['target'] = meas_data['target'] + meas_data['HP{}Target'.format(i)]
for powerpoint in powerpoints:

    baseline['power'] = baseline['power'] + baseline[powerpoint]/1000.
    
#    control['power'] = control['power'] + control[powerpoint]/1000.

    rtp['power'] = rtp['power'] + rtp[powerpoint]/1000.
sum11=0
sum22=0
sum33=0
for i in range(30):

   baseline_sec = baseline['power'][i*1440:(i+1)*1440].tolist()
   # meas_data_sec = meas_data['target'][i*1440:(i+1)*1440].tolist()
   # control_sec = control['power'][i*1440:(i+1)*1440].tolist()
   rtp_sec = rtp['power'][i*1440:(i+1)*1440].tolist()
#   print(len(rtp_sec))
   sum1= 0
   # sum2 = 0
   sum3 = 0
   for s in range(len(baseline_sec)):
       sum1=sum1+ baseline_sec[s]*price['price'].iloc[s]
       # sum2=sum2+ control_sec[s]*price['price'].iloc[s] 
       sum3=sum3+ rtp_sec[s]*price['price'].iloc[s]
#       meas_data_sec[s] = meas_data_sec[s]/1000.
   sum11=sum11+ sum1   
   # sum22=sum22+ sum2   
   sum33=sum33+ sum3   
   fig, (ax1,ax3) = plt.subplots(2, sharex=True)
   
   x = pd.date_range(start='8/1/2017 00:00:00', end='8/2/2017 00:00:00',freq='1min')[:-1]
   
   dates =  matplotlib.dates.date2num(x)
   
   tab = pd.DataFrame()
   
   tab['baseline'] = baseline_sec
   

   tab['rtp'] = rtp_sec
   
   if sum1 >0:

      ax1.plot_date(dates,tab['baseline'].rolling(window=30).mean(),linestyle='-',label='baseline',marker='')
      ax1.plot_date(dates,tab['rtp'].rolling(window=30).mean(),linestyle='-',label='rtp:{}%'.format(round(100-(sum3/sum1)*100)),marker='')
#      ax2.plot_date(dates,tab['control'].rolling(window=30).mean(),linestyle='-',label='control',marker='')
#      ax2.plot_date(dates,meas_data_sec,linestyle='-.',label='target',marker='')

 
      ax3.plot_date(dates,price['price'],linestyle='-',label='control',marker='')
      myFmt = mdates.DateFormatter('%H:%M')
      ax3.xaxis.set_major_formatter(myFmt)
      ax1.legend(loc='best')
      plt.savefig('case_{}.png'.format(i))
   
# print(round(100-(sum22/sum11)*100))
# print(round(100-(sum22/sum33)*100))
