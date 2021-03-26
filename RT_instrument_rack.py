


import numpy as np
import matplotlib.pyplot as plt

import time

from helper_functions import * 
from measurement_routines import * 



def main():

	rm = visa.ResourceManager()
        
	print(rm.list_resources())

	
	ramp_time = 1
	quick_psu_ramp(rm, I_amps= 30, up_ramp_time = ramp_time, dwell_time = 30, down_ramp_time = ramp_time, setup_time = 5)


	#Fire Heater
	# pulse_duration = 0.5 # seconds
	# init_heater()
	# fire_heater(pulse_duration)


	

	return




def top_control_IV_curve(rm):

# #Run IV curve, measure both up and down ramps
	test_code = 'corc_Bz_jan_20210'

	#Initialize instruments
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage = 3)

	#Ramp up and down
	safe_mode = False
	I_start = 0
	I_max = 375
	dA = 5
	
	#ramp up then turn off
	# run_IV_curve(rm, nanovm, dvm, sorenson, I_start, I_max, dA, test_code, True, safe_mode) #ramp up, leave PSU energized

	#Ramp up and down
	run_IV_curve(rm, nanovm, dvm, sorenson, I_start, I_max, dA, test_code, False, safe_mode) #ramp up, leave PSU energized
	time.sleep(0.1)
	run_IV_curve(rm, nanovm, dvm, sorenson, I_max, I_start, -dA, test_code, True, safe_mode) #ramp up, leave PSU energized


# Ramp PSU for CORC quench tests
	# quick_psu_ramp(rm, I_amps= 10, up_ramp_time = 0.5, dwell_time = 1, down_ramp_time = 0.5, setup_time = 10)



	return








if __name__ == "__main__": main()



