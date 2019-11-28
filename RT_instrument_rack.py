


# import serial
import sys
import os
import time
import visa

import numpy as np
import matplotlib.pyplot as plt

from helper_functions import * 
from measurement_routines import * 




def main():

#Create a results folder
	dir_name = create_results_folder(test_code_0='test_tape')


#Initialize instruments
	rm = visa.ResourceManager()
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage=3)


#Run IV curve
	time_array, I_shunt, Vsample_1, Vsample_2 = run_IV_curve(nanovm, dvm, sorenson, dir_name, I_start=0, I_end=100, I_inc=5)


#Analye IV curve
	print('Ch1 analysis')
	offset_ch1, resistance_ch1, Ic_ch1, n_ch1 = curve_fit_IV(I_shunt, Vsample_1, Ic_guess=1000, V_criterion=1e-6)
	print('Ch2 analysis')
	offset_ch2, resistance_ch2, Ic_ch2, n_ch2 = curve_fit_IV(I_shunt, Vsample_2, Ic_guess=1000, V_criterion=1e-6)



	disable_sorenson(sorenson_psu)


	return





if __name__ == "__main__": main()