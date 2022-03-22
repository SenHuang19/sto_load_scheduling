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


points = ['SOUTH PERIM SPC TS11_COOL 1/0','East Perim Spc TE12_Cool 1/0','North Perim Spc TN13_Cool 1/0','West Perim Spc TW14_Cool 1/0','Core Spc TC15_Cool 1/0','South Perim Spc GS1_Cool 1/0','East Perim Spc GE2_Cool 1/0','North Perim Spc GN3_Cool 1/0','West Perim Spc GW4_Cool 1/0','Core Spc GC5_Cool 1/0']




for i in range(30): 

#dates2 =  matplotlib.dates.date2num(price['ts'].tolist())
    fig, (ax1,ax2) = plt.subplots(2, sharex=True)
    x = pd.date_range(start='8/1/2017 00:00:00', end='8/2/2017 00:00:00',freq='1min')[:-1]
   
    dates =  matplotlib.dates.date2num(x)
    for s in range(len(points)):
       ax1.plot_date(dates,rtp['{}:Schedule Value [](TimeStep)'.format(points[s].upper())][i*1440:(i+1)*1440],linestyle='-',label='rtp',marker='')
#       ax2.plot_date(dates,control['{}:Schedule Value [](TimeStep)'.format(points[s].upper())][i*1440:(i+1)*1440],linestyle='-',label='rtp',marker='')
    ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())][i*1440:(i+1)*1440]-2,linestyle='-.',label='control',marker='')
    ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())][i*1440:(i+1)*1440]+2,linestyle='-.',label='control',marker='')
    ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())][i*1440:(i+1)*1440]-2,linestyle='-.',label='control',marker='')
    ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())][i*1440:(i+1)*1440]+2,linestyle='-.',label='control',marker='')
    myFmt = mdates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(myFmt)
    plt.savefig('case_{}_temp.png'.format(i))