import pandas as pd
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import datetime
import matplotlib.pyplot as plt
import csv

case = 'Case1 - length=30'

control = pd.read_csv(case+'/Others/eplusout.csv')

points = ['South Perim Spc TS11','East Perim Spc TE12','North Perim Spc TN13','West Perim Spc TW14','Core Spc TC15','South Perim Spc GS1','East Perim Spc GE2','North Perim Spc GN3','West Perim Spc GW4','Core Spc GC5']

control=control.groupby(np.arange(len(control))//60).mean()


control['ts'] = pd.date_range(start='8/1/2017 00:00:00', end='8/30/2017 23:59:00',freq='60min')
print(len(control))
# hour_id = []
# pred_id = []
# zone_id = []
# oda_temp  = []
# real_temp = []
# delta_temp= []
N = 30 # number of days in simulation results
for z in range(len(points)):
   hour_id = []
   pred_id = []
   zone_id = []
   oda_temp  = []
   real_temp = []
   delta_temp= []
   for start_hour in range(1,24*(N-1)+1,1):
      prediction = pd.read_csv(case+'/saved/sol_T{}.csv'.format(int(start_hour*60)))
      for tt in range(24):
         hr = start_hour+tt
         pred_id.append(tt+1)
         hour_id.append(hr%24)
         zone_id.append(z)
         oda_temp.append(prediction.iloc[tt+1]['OutdoorTemperature'])
         # print(hr)
         Treal = control.iloc[hr]['{}:Zone Mean Air Temperature [C](TimeStep)'.format(points[z].upper())]
         real_temp.append(Treal)
         Tpred = prediction.iloc[tt+1]['sol_tzon_'+str(z+1)]
         Tdelta = Treal - Tpred
         delta_temp.append(Tdelta)
      # dates =  matplotlib.dates.date2num(control['ts'].tolist())

      # # #dates2 =  matplotlib.dates.date2num(price['ts'].tolist())
      # for i in range(len(points)):
      #    prediction['sol_tzon_{}_corr'.format(i+1)] = prediction['sol_tzon_{}'.format(i+1)] + prediction['Tdelta_{}'.format(i+1)] 

      # for i in range(len(points)):
      #    fig, (ax1) = plt.subplots(1, sharex=True)
      #    ax1.plot_date(dates,control['{}:Zone Mean Air Temperature [C](TimeStep)'.format(points[i].upper())],linestyle='-',label='rea',marker='x')
      #    ax1.plot_date(dates[start_hour+1:],prediction['sol_tzon_{}'.format(i+1)][:24-start_hour-1],linestyle='-.',label='pre',marker='.')
      #    ax1.plot_date(dates[start_hour+1:],prediction['sol_tzon_{}_corr'.format(i+1)][:24-start_hour-1],linestyle='-.',label='cor',marker='.')
      # # ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]-2,linestyle='-.',label='control',marker='')
      # # ax1.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]+2,linestyle='-.',label='control',marker='')
      # # ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]-2,linestyle='-.',label='control',marker='')
      # # ax2.plot_date(dates,baseline['{}:Schedule Value [](TimeStep)'.format(points[0].upper())]+2,linestyle='-.',label='control',marker='')
      #    ax1.legend()
      #    myFmt = mdates.DateFormatter('%H:%M')
      #    ax1.xaxis.set_major_formatter(myFmt)
      #    plt.savefig('z{}.png'.format(i))

# prediction_all = pd.DataFrame({'HourIndex':hour_id,'PredictionIndex':pred_id,'ZoneIndex':zone_id,'OutdoorAirTemperature':oda_temp,'RealTemperature':real_temp,'Tdelta':delta_temp})
# prediction_all.to_csv('prediction_all.csv')


   fig = plt.figure()
   ax1 = fig.add_subplot(projection='3d')
   # x, y = np.random.rand(2, 100) * 4
   x  = np.array(delta_temp)
   y1 = np.array(hour_id) # np.array([h%24 for h in hour_id])
   hist1, xedges1, yedges1 = np.histogram2d(x, y1, bins=[60,24], range=[[-3, 3], [0, 23]])

   # Construct arrays for the anchor positions of the 16 bars.
   xpos1, ypos1 = np.meshgrid(xedges1[:-1] + 0.25, yedges1[:-1] + 0.25, indexing="ij")
   xpos1 = xpos1.ravel()
   ypos1 = ypos1.ravel()
   zpos1 = 0

   # Construct arrays with the dimensions for the 16 bars.
   dx1 = dy1 = 0.5 * np.ones_like(zpos1)
   dz1 = hist1.ravel()

   ax1.bar3d(xpos1, ypos1, zpos1, dx1, dy1, dz1, zsort='average')
   plt.savefig('hist1_z{}.png'.format(z+1))
   # plt.show()


   
   fig = plt.figure()
   ax2 = fig.add_subplot(projection='3d')
   # x, y = np.random.rand(2, 100) * 4
   x  = np.array(delta_temp)
   y2 = np.array(pred_id)
   hist2, xedges2, yedges2 = np.histogram2d(x, y2, bins=[60,24], range=[[-3, 3], [1, 24]])

   # Construct arrays for the anchor positions of the 16 bars.
   xpos2, ypos2 = np.meshgrid(xedges2[:-1] + 0.25, yedges2[:-1] + 0.25, indexing="ij")
   xpos2 = xpos2.ravel()
   ypos2 = ypos2.ravel()
   zpos2 = 0

   # Construct arrays with the dimensions for the 16 bars.
   dx2 = dy2 = 0.5 * np.ones_like(zpos2)
   dz2 = hist2.ravel()

   ax2.bar3d(xpos2, ypos2, zpos2, dx2, dy2, dz2, zsort='average')
   plt.savefig('hist2_z{}.png'.format(z+1))
   # plt.show()
   
   

   fig = plt.figure()
   ax3 = fig.add_subplot(projection='3d')
   # x, y = np.random.rand(2, 100) * 4
   x  = np.array(delta_temp)
   y3 = np.array(oda_temp)
   hist3, xedges3, yedges3 = np.histogram2d(x, y3, bins=[60,60], range=[[-3, 3], [5, 38]])

   # Construct arrays for the anchor positions of the 16 bars.
   xpos3, ypos3 = np.meshgrid(xedges3[:-1] + 0.25, yedges3[:-1] + 0.25, indexing="ij")
   xpos3 = xpos3.ravel()
   ypos3 = ypos3.ravel()
   zpos3 = 0

   # Construct arrays with the dimensions for the 16 bars.
   dx3 = dy3 = 0.5 * np.ones_like(zpos3)
   dz3 = hist3.ravel()

   ax3.bar3d(xpos3, ypos3, zpos3, dx3, dy3, dz3, zsort='average')
   plt.savefig('hist3_z{}.png'.format(z+1))
   # plt.show()
