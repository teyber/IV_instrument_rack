


# import serial
import sys
import os
import time
import visa
import numpy as np
import matplotlib.pyplot as plt






def get_meter_voltages(nanovm, dvm):

#Ask meters for readings
	print(get_nanovm(nanovm, ch_num = 1))
	print(get_nanovm(nanovm, ch_num = 2))
	print(get_dvm(dvm))

	return





def run_IV_curve(nanovm, dvm, sorenson, dir_name, I_start, I_end, I_inc):

	#IV parameters
	t_dwell = 0.1 #50 milliseconds
	V_sample_max = 1e-3 	


	I_vec = np.arange(I_start, I_end + I_inc, I_inc)
	if np.min(I_vec) < 0:
		print('Error: current set point is less than 0')
		return

	num_points = np.size(I_vec)

	#Initialize vectors to be filled in IV curve
	I_shunt = np.zeros(num_points)
	Vsample_1 = np.zeros(num_points)
	Vsample_2 = np.zeros(num_points)
	time_array = np.zeros()

	#Check starting point before telling power supply to ramp
	check_sample1 = get_nanovm(nanovm, ch_num = 1)
	check_sample2 = get_nanovm(nanovm, ch_num = 2)
	if (np.abs(check_sample1) > V_sample_max):
		print('Error! Channel 1 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, check_sample1, check_sample2)

	if (np.abs(check_sample2) > V_sample_max):
		print('Error! Channel 2 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, check_sample1, check_sample2)


	#Start IV curve
	for i in np.arange(num_points):

		#Set power supply to next current
		set_sorenson_psu(sorenson_psu, I_vec[i])

		#Dwell to eliminate inductive voltage
		time.sleep(t_dwell)

		#Get voltages from meters
		time_array[i] = time.time()
		I_shunt[i] = get_dvm(dvm)[1]
		Vsample_1[i] = get_nanovm(nanovm, ch_num = 1)
		Vsample_2[i] = get_nanovm(nanovm, ch_num = 1)


		#See if voltage threshold has been exceeded. If so, set PSU to 0 amps.
		if (np.max((np.abs(Vsample_1[i]),np.abs(Vsample_1[i]))) > V_sample_max):
			set_sorenson_psu(sorenson_psu, 0)
			print('WARNING: sample threshold has been exceeded!')
			print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[i], Vsample_2[i])

			break

		#Plot curve 


	#save output
	code_num = 1
	if os.path.exists(dir_name + '\\' + 'IV_curve_' + str(code_num)):
		code_num += 1
	else:
		np.savetxt('IV_curve_' + str(code_num) + '.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))	
	


	return








#Create a folder for the experiment
def create_results_folder(test_code_0):

	keep_trying = True
	code_num = 1
	dir_name = 'Results\\' + test_code_0 + '_' + str(code_num)

	#Find a unique number in the results folder and create a new directory
	while keep_trying == True:

		test_code = test_code_0 + '_' + str(code_num)
		dir_name = 'Results\\'+ test_code

		if code_num > 1e6:
			print('Error! Enormous amount of folders created')
			print('Please fix error and try again')

		elif os.path.exists(dir_name):
			code_num += 1

		else:
			os.makedirs(dir_name)
			keep_trying = False


	return dir_name




