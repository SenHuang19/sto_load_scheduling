''' Generic Interface '''

import json, time, datetime

import pandas as pd

import requests

import ast

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


rawdf = pd.read_csv('SmallOffice.csv')
Toa = rawdf["Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)"].values.tolist()
Tzon1 = rawdf["SOUTH PERIM SPC GS1:Zone Mean Air Temperature [C](TimeStep)"]
Tzon2 = rawdf["EAST PERIM SPC GE2:Zone Mean Air Temperature [C](TimeStep)"]
Tzon3 = rawdf["NORTH PERIM SPC GN3:Zone Mean Air Temperature [C](TimeStep)"]
Tzon4 = rawdf["WEST PERIM SPC GW4:Zone Mean Air Temperature [C](TimeStep)"]
Tzon5 = rawdf["CORE SPC GC5:Zone Mean Air Temperature [C](TimeStep)"]

Tzon6 = rawdf["SOUTH PERIM SPC TS11:Zone Mean Air Temperature [C](TimeStep)"]
Tzon7 = rawdf["EAST PERIM SPC TE12:Zone Mean Air Temperature [C](TimeStep)"]
Tzon8 = rawdf["NORTH PERIM SPC TN13:Zone Mean Air Temperature [C](TimeStep)"]
Tzon9 = rawdf["WEST PERIM SPC TW14:Zone Mean Air Temperature [C](TimeStep)"]
Tzon10 = rawdf["CORE SPC TC15:Zone Mean Air Temperature [C](TimeStep)"]

TSzon1 = rawdf["SOUTH PERIM SPC GS1:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon2 = rawdf["EAST PERIM SPC GE2:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon3 = rawdf["NORTH PERIM SPC GN3:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon4 = rawdf["WEST PERIM SPC GW4:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon5 = rawdf["CORE SPC GC5:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()

TSzon6 = rawdf["SOUTH PERIM SPC TS11:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon7 = rawdf["EAST PERIM SPC TE12:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon8 = rawdf["NORTH PERIM SPC TN13:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon9 = rawdf["WEST PERIM SPC TW14:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()
TSzon10 = rawdf["CORE SPC TC15:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)"].values.tolist()

for t in range(600,720,60):
	input_dict = {
		"OutdoorAirTemperature" : Toa[t],
		"Time"    : (t-600)*60+3540,
		"forecast": Toa[t+60:(t+24*60+1):60],
		"Tzon1"   : Tzon1[t],
		"Tzon2"   : Tzon2[t],
		"Tzon3"   : Tzon3[t],
		"Tzon4"   : Tzon4[t],
		"Tzon5"   : Tzon5[t],
		"Tzon6"   : Tzon6[t],
		"Tzon7"   : Tzon7[t],
		"Tzon8"   : Tzon8[t],
		"Tzon9"   : Tzon9[t],
		"Tzon10"  : Tzon10[t],
		"Trzon1"  : TSzon1[t+60:(t+24*60+1):60],
		"Trzon2"  : TSzon2[t+60:(t+24*60+1):60],
		"Trzon3"  : TSzon3[t+60:(t+24*60+1):60],
		"Trzon4"  : TSzon4[t+60:(t+24*60+1):60],
		"Trzon5"  : TSzon5[t+60:(t+24*60+1):60],
		"Trzon6"  : TSzon6[t+60:(t+24*60+1):60],
		"Trzon7"  : TSzon7[t+60:(t+24*60+1):60],
		"Trzon8"  : TSzon8[t+60:(t+24*60+1):60],
		"Trzon9"  : TSzon9[t+60:(t+24*60+1):60],
		"Trzon10" : TSzon10[t+60:(t+24*60+1):60]}

	with open('./input.json','w') as f:
		json.dump(input_dict, f)
	# print(input_dict["Trzon2"])
	work('http://127.0.0.1:5000')
