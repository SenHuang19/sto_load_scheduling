import os
import subprocess
from shutil import copyfile

import time
start_time = time.time()




modelPath = 'Small_Office.idf'
weatherPath = 'USA_WA_Pasco-Tri.Cities.AP.727845_TMY3.epw'

os.environ['BCVTB_HOME'] = 'bcvtb'

print(os.name)
if os.name == 'nt':
   cmdStr = "C:\EnergyPlusV8-4-0\energyplus -w \"%s\" -r \"%s\"" % (weatherPath, modelPath)
else:
   cmdStr = "energyplus -w \"%s\" -r \"%s\"" % (weatherPath, modelPath)

sock = subprocess.Popen('python rtp.py'+' '+'Small_Office.idf'+' '+'ep_small_office.config', shell=False)
#sock = subprocess.Popen('python master_nn.py'+' '+'BRSW2.idf'+' '+'ep_BRSW2.config', shell=False)
simulation = subprocess.Popen(cmdStr, shell=True)
simulation.wait()
time.sleep(15)
sock.terminate()
copyfile('eplusout.csv', 'rtp.csv')
print("--- %s seconds ---" % (time.time() - start_time))