import pandas as pd
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import datetime
import matplotlib.pyplot as plt
import csv

case = 'Case1 - length=30'

start_hour = 12

prediction = pd.read_csv(case+'/saved/sol_T{}.csv'.format(int(start_hour*60)))

control = pd.read_csv(case+'/Others/eplusout.csv')


points = ['South Perim Spc TS11','East Perim Spc TE12','North Perim Spc TN13','West Perim Spc TW14','Core Spc TC15','South Perim Spc GS1','East Perim Spc GE2','North Perim Spc GN3','West Perim Spc GW4','Core Spc GC5']

control=control.groupby(np.arange(len(control))//60).mean()


control['ts'] = pd.date_range(start='8/1/2017 00:00:00', end='8/1/2017 23:59:00',freq='60min')


dates =  matplotlib.dates.date2num(control['ts'].tolist())

# #dates2 =  matplotlib.dates.date2num(price['ts'].tolist())
for i in range(len(points)):
     prediction['sol_tzon_{}_corr'.format(i+1)] = prediction['sol_tzon_{}'.format(i+1)] + prediction['Tdelta_{}'.format(i+1)] 

for i in range(len(points)):
   fig, (ax1) = plt.subplots(1, sharex=True)
   ax1.plot_date(dates,control['{}:Zone Mean Air Temperature [C](TimeStep)'.format(points[i].upper())],linestyle='-',label='rea',marker='x')
   ax1.plot_date(dates[start_hour+1:],prediction['sol_tzon_{}'.format(i+1)][:24-start_hour-1],linestyle='-.',label='pre',marker='.')
   ax1.plot_date(dates[start_hour+1:],prediction['sol_tzon_{}_corr'.format(i+1)][:24-start_hour-1],linestyle='-.',label='cor',marker='.')
# ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]-2,linestyle='-.',label='control',marker='')
# ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]+2,linestyle='-.',label='control',marker='')
# ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]-2,linestyle='-.',label='control',marker='')
# ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]+2,linestyle='-.',label='control',marker='')
   ax1.legend()
   myFmt = mdates.DateFormatter('%H:%M')
   ax1.xaxis.set_major_formatter(myFmt)
   plt.savefig('z{}.png'.format(i))