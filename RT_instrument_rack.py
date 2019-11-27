


# import serial
import sys
import time
import visa

import numpy as np
import matplotlib.pyplot as plt

from helper_functions import * 

rm = visa.ResourceManager()



max_voltage = 1.0 #Max voltage of 0.2 volts

I_ramp_time = 0.1 #seconds
I_ramp_mag = 1000 #amps
peak_dwell_time = 0.2 #seconds




def main():

	test_comm()




#Initialize instruments
	
	nanovm = init_nanovm()
	dvm = init_dvm()
	sorenson = init_sorenson_psu(max_voltage=3)



#Ask meters for readings

	print(get_nanovm(nanovm, ch_num = 1))
	print(get_nanovm(nanovm, ch_num = 2))
	print(get_dvm(dvm))


	return











if __name__ == "__main__": main()