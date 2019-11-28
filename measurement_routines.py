


# import serial
import sys
import os
import time
import visa
import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import interp1d
from scipy.optimize import differential_evolution





##########################################################################################
#IC curve

def run_IV_curve(nanovm, dvm, sorenson, dir_name, I_start, I_end, I_inc):

	#IV parameters
	t_dwell = 0.2 #200 milliseconds
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
	time_array[0] = time.time()
	I_shunt[0] = get_dvm(dvm)[1]
	Vsample_1[0] = get_nanovm(nanovm, ch_num = 1)
	Vsample_2[0] = get_nanovm(nanovm, ch_num = 2)


	if (np.abs(Vsample_1[0]) > V_sample_max):
		print('Error! Channel 1 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[0], Vsample_2[0])
		return

	if (np.abs(Vsample_2[0]) > V_sample_max):
		print('Error! Channel 2 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[0], Vsample_2[0])
		return


	#Create a figure that will be updated live
	fig = plt.figure(figsize=(8,6))
	ax1 = fig.add_subplot(1, 1, 1)
	plt.ion()

	L1, = ax1.plot(I_shunt, Vsample_1, 'k', label = 'Ch1')
	L2, = ax1.plot(I_shunt, Vsample_2, 'b', label = 'Ch2')

	#Range for plotting
	x_min = I_start-5
	x_max = I_end+20
	y_min = -5e-6
	y_max = 100e-6

	ax1.set_xlim([I_start-5, I_end+20])
	ax1.set_ylim([-1e-6, 1e-3])
	ax1.legend()

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

		#Print values. Could be used to recover valuable data if program crashes
		print(i, time_array[i], I_shunt[i], Vsample_1[i], Vsample_2[i])

		#See if voltage threshold has been exceeded. If so, set PSU to 0 amps.
		if (np.max((np.abs(Vsample_1[i]),np.abs(Vsample_1[i]))) > V_sample_max):
			set_sorenson_psu(sorenson_psu, 0)
			print('WARNING: sample threshold has been exceeded!')
			print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[i], Vsample_2[i])
			time.sleep(0.1)
			break

		#Plot curve, update y axis limits if necesarry
		if (np.max(Vsample_1) > y_max) or (np.max(Vsample_2) > y_max): 
			y_max = np.max((np.max(Vsample_1), np.max(Vsample_2)))

		if (np.min(Vsample_1) < y_min) or (np.min(Vsample_2) < y_min): 
			y_min = np.min((np.min(Vsample_1), np.min(Vsample_2)))

		ax1.set_ylim([y_min, y_max])
		L1.set_ydata(Vsample_1[0:i])
		L1.set_xdata(I_shunt[0:i])
		L2.set_ydata(Vsample_2[0:i])
		L2.set_xdata(I_shunt[0:i])

		plt.pause(0.01)


	plt.show()
	plt.savefig('plot_IV_curve.pdf')
	plt.close()


	#Ramp down, do not collect voltages along way
	time.sleep(0.1)
	down_ramp_time = 5
	print('IV curve complete. Beginning ramp down for ' + str(down_ramp_time) + ' seconds')
	ramp_sorenson_psu(sorenson_psu, I_ramp_time=down_ramp_time, I_ramp_mag=0)
	time.sleep(down_ramp_time+1)
	modify_sorenson_limits(sorenson_psu, max_I=0, max_V=0)


	#save output
	code_num = 1
	if os.path.exists(dir_name + '\\' + 'IV_curve_' + str(code_num)):
		code_num += 1
	else:
		np.savetxt('IV_curve_' + str(code_num) + '.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))	
	

	return time_array, I_shunt, Vsample_1, Vsample_2




#Simple but useful function to print current voltages at start of IV curve or during cooldown 
def get_meter_voltages(nanovm, dvm):

	print(get_nanovm(nanovm, ch_num = 1))
	print(get_nanovm(nanovm, ch_num = 2))
	print(get_dvm(dvm))

	return



#End IV curve
##########################################################################################




##########################################################################################
#Start IV curve fit

#fit to DC offset, linear resistance, Ic and n value
def curve_fit_IV(I_meas, V_meas, Ic_guess, V_criterion):

	#Voltage offset, linear resistance, Ic and n value
	bnds = ((-10e-3,10e-3), (1e-10,10e-3),(0.1*Ic_guess, 2*Ic_guess),(10,40))
	sol = differential_evolution(curve_fit_obj, bounds = bnds_long, args = (I_meas, V_meas, V_criterion), strategy='best1bin', maxiter=200, popsize=300, tol=1e-4, seed=False, mutation=(0, 0.2), recombination=0.4, disp=False, polish = True, init = 'random', updating = 'deferred', workers = 3)

	offset_fit = sol.x[0]
	resistance_fit = sol.x[1]
	Ic_fit = sol.x[2]
	n_fit = sol.x[3]

	print('\n')
	print('********************')
	print('Optimization convergence: ', sol.fun)
	print('Voltage offset [micro-V]: ', offset_ch1)
	print('Resistance [micro-ohm]: ', resistance_ch1)
	print('Critical current [Amps]: ', Ic_ch1)
	print('n value [-]: ', n_ch1)
	print('********************')
	print('\n')

	return offset_fit, resistance_fit, Ic_fit, n_fit




#Objective function to be called in curve fit optimizer
def curve_fit_obj(x, current, V_raw, V_criterion):
	#fit DC offset, linear resistance and SC contribution

	#x - offset, resistance, Ic, n
	V = x[0] + current*x[1] + V_criterion*(np.power(current/x[2],x[3]))

	nan_index = np.argwhere(current<0)
	V[nan_index] = 0
	V_raw[nan_index] = 0

	err_val = np.linalg.norm(V-V_raw)
	return err_val
		


#End IV curve fit
##########################################################################################






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





