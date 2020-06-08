


import numpy as np
import matplotlib.pyplot as plt

import time

from helper_functions import * 
from measurement_routines import * 



def main():

	rm = visa.ResourceManager()
	

# #monitor cooldown
# 	monitor_cooldown(rm)


# #Run IV curve, measure both up and down ramps
	test_code = 'corc_june_9_2020'

	#Initialize instruments
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage = 3)

	#Ramp up and down
	safe_mode = True
	I_max = 40
	dA = 5
	run_IV_curve(rm, nanovm, dvm, sorenson, 0, I_max, dA, test_code, disable_psu = False, safe_mode) #ramp up, leave PSU energized
	time.sleep(0.1)
	run_IV_curve(rm, nanovm, dvm, sorenson, I_max, 0, -dA, test_code, disable_psu = True, safe_mode) #ramp up, leave PSU energized


# Ramp PSU for CORC quench tests
	# quick_psu_ramp(rm, I_amps= 10, up_ramp_time = 0.5, dwell_time = 1, down_ramp_time = 0.5, setup_time = 10)



	return








if __name__ == "__main__": main()



