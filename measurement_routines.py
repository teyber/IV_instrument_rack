


# import serial
import os
import time
import visa
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution

from helper_functions import * 



##########################################################################################
#Start Yokogowa ramp

def quick_psu_ramp(rm, I_amps, up_ramp_time, dwell_time, down_ramp_time, setup_time):

	sorenson = init_sorenson_psu(rm, max_voltage=5)

	if setup_time < 5:
		print('You have not allowed enough time to go to yokogawa: ', setup_time)
		return

# Safety check
	print('------------ Safety check ------------')
	print('Programmed current range [A]: ', I_amps)
	print('up ramp, dwell, down ramp [s]: ', up_ramp_time, dwell_time, down_ramp_time)
	print('0 - Exit')		
	print('1 - Energize systems')
	current_warning = int(input('Is this correct? '))
	if current_warning == 1: 
		print('Continuing with IV curve - systems will be energized')
	else: 
		return

	#countdown to energization
	for i in np.arange(int(setup_time)):
		print('Energizing in :', int(setup_time)-i)
		time.sleep(1)

	time.sleep(2)

	ramp_sorenson_psu(sorenson, up_ramp_time, I_amps) #linear ramp up
	time.sleep(up_ramp_time + dwell_time) 

	ramp_sorenson_psu(sorenson, down_ramp_time, 0) #Ramp to 0 amps over 0.1 seconds



	return


#End Yokogowa ramp
##########################################################################################









##########################################################################################
#IV curve

def run_IV_curve(rm, nanovm, dvm, sorenson_psu,	I_start, I_end, I_inc, test_code, disable_psu = True, safe_mode = True):


	#IV parameters
	I_vec = np.arange(I_start, I_end + I_inc, I_inc)
	V_sample_max = 1 #Disable PSU if voltage exceeds this
	t_settle = 2 #time to wait before recording voltage
	t_plot = 1 #time to plot
	inter_point_ramp_time = 2

	#Create a folder for this result (see helper_functions)
	dir_name = create_folder(test_code)


	# Ask user to double check current range before proceeding
	print('------------ Safety check ------------')
	print('Programmed current range [A]: ', I_vec)
	print('Programmed voltage threshold [V], ramp time [s], settle time [s]: ', V_sample_max, inter_point_ramp_time, t_settle)
	print('MANUALLY CHECK SHUNT RESISTOR IN GET_DVM()!')
	print('0 - Exit')		
	print('1 - Energize systems')
	current_warning = int(input('Is this correct? '))
	if current_warning == 1: 
		print('Continuing with IV curve - systems will be energized')
	else: 
		ramp_sorenson_psu(sorenson_psu, 1, 0) #Ramp to 0 amps over 0.5 seconds
		return

	#Initialize vectors to be filled in IV curve
	num_points = np.size(I_vec)
	I_shunt = np.zeros(num_points)
	Vsample_1 = np.zeros(num_points)
	Vsample_2 = np.zeros(num_points)
	time_array = np.zeros(num_points)

	#Check starting point before telling power supply to ramp
	time_array[0] = time.time()
	I_shunt[0] = get_dvm(dvm)[1]
	Vsample_1[0] = get_nanovm(nanovm, ch_num = 1)
	Vsample_2[0] = get_nanovm(nanovm, ch_num = 2)



	if (np.abs(Vsample_1[0]) > V_sample_max):
		print('Error! Channel 1 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[0], Vsample_2[0])
		ramp_sorenson_psu(sorenson_psu, I_ramp_time=2, I_ramp_mag=0)
		return 0, 0, 0, 0

	if (np.abs(Vsample_2[0]) > V_sample_max):
		print('Error! Channel 2 is greater than voltage threshold. Returning to main.')
		print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[0], Vsample_2[0])
		ramp_sorenson_psu(sorenson_psu, I_ramp_time=2, I_ramp_mag=0)
		return 0, 0, 0, 0



	#Range for plotting
	x_min = I_start-5
	x_max = I_end+20
	y_min = -75e-6
	y_max = -50e-6



	#Start IV curve UP
	for i in np.arange(num_points):
		print(i)
		#Set power supply to next current
		ramp_sorenson_psu(sorenson_psu, inter_point_ramp_time, I_ramp_mag=I_vec[i]) # set_sorenson_psu(sorenson_psu, I_vec[i])

		#Dwell to eliminate inductive voltage
		time.sleep(t_settle + inter_point_ramp_time)

		#Get voltages from meters
		time_array[i] = time.time()
		I_shunt[i] = get_dvm(dvm)[1]
		Vsample_1[i] = get_nanovm(nanovm, ch_num = 1)
		Vsample_2[i] = get_nanovm(nanovm, ch_num = 2)


		#Flip sign
		# Vsample_1[i] = -Vsample_1[i]

		print('WARNING - FORCING CHANNEL 2 OFF ON PSU')
		Vsample_2[0] = 0
		Vsample_2[i] = 0

		#Print values. Could be used to recover valuable data if program crashes
		print('I, V1, V2', I_shunt[i], Vsample_1[i], Vsample_2[i])

		#See if voltage threshold has been exceeded. If so, set PSU to 0 amps.
		if ((np.abs(Vsample_1[i]) >= V_sample_max) or (np.abs(Vsample_2[i]) >= V_sample_max)):
			ramp_sorenson_psu(sorenson_psu, 0.5, 0) #Ramp to 0 amps over 0.5 seconds
			print('WARNING: sample threshold has been exceeded!')
			print('V_sample_max, V_sample1, V_sample2: ', V_sample_max, Vsample_1[i], Vsample_2[i])
			np.savetxt(dir_name + '\\' +'EXCEEDED_IV_curve_.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))
			return 0, 0, 0, 0

		#Plot curve, update y axis limits if needed
		# if (np.max(Vsample_1) > y_max) or (np.max(Vsample_2) > y_max): 
		# 	y_max = np.max((np.max(Vsample_1), np.max(Vsample_2)))


		# if (np.min(Vsample_1) < y_min) or (np.min(Vsample_2) < y_min): 
		# 	y_min = np.min((np.min(Vsample_1), np.min(Vsample_2)))


		y_min = np.min(Vsample_1)
		y_max = np.max(Vsample_2)

	
		fig = plt.figure(figsize=(8,6))
		plt.plot(I_shunt[0:(i+1)], 1000*Vsample_1[0:(i+1)], 'ko--', label = 'Ch1')
		# plt.plot(I_shunt[0:(i+1)], 1000*Vsample_2[0:(i+1)], 'bo--', label = 'Ch2')
		plt.ylim([1000*y_min, 1000*y_max])
		plt.xlabel('I [A]')
		plt.ylabel('V [mV]')
		# plt.legend()
		plt.show(block=False)
		# plt.show()

		plt.pause(t_plot)
		plt.close()

		# In safe mode, require user input to go to next point
		if safe_mode == True:
			print('Continue ramping?')
			current_warning = int(input('Exit (0), or continue(1)'))
			if current_warning != 1:
				ramp_sorenson_psu(sorenson_psu, 0.5, 0) #Ramp to 0 amps over 0.5 seconds
				print('returning to main')
				np.savetxt(dir_name + '\\' +'CANCELLED_IV_curve_.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))
				return 0, 0, 0, 0
	

	#Ramp down, do not collect voltages along way

	if disable_psu  == True: #if we are not going to ramp down
		time.sleep(0.1)
		down_ramp_time = 2
		print('IV curve complete. Disabling PSU')
		ramp_sorenson_psu(sorenson_psu, I_ramp_time=2, I_ramp_mag=0)
		time.sleep(down_ramp_time+1)
		modify_sorenson_limits(sorenson_psu, max_I=0, max_V=0)

	else: 
		print('IV curve complete. WARNING - Leaving power supply energized for down ramp')



#Analye IV curve with curve fit
	Ic_guess = 180 #amps

	print('Ch1 analysis')
	offset_ch1, resistance_ch1, Ic_ch1, n_ch1 = curve_fit_IV(I_shunt, Vsample_1, Ic_guess, V_criterion=1e-6)
	
	print('Ch2 analysis')
	offset_ch2, resistance_ch2, Ic_ch2, n_ch2 = curve_fit_IV(I_shunt, Vsample_2, Ic_guess, V_criterion=1e-6)

	#save output
	np.savetxt(dir_name + '\\' +'IV_curve.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))	
	np.savetxt(dir_name + '\\' +'ch1_fit.txt', [offset_ch1, resistance_ch1, Ic_ch1, n_ch1])	
	np.savetxt(dir_name + '\\' +'ch2_fit.txt', [offset_ch2, resistance_ch2, Ic_ch2, n_ch2])	

	#Save figure

	fig = plt.figure(figsize=(8,6))
	plt.plot(I_shunt, 1000*Vsample_1, 'ko--', label = 'Ch1')
	# plt.plot(I_shunt, 1000*Vsample_2, 'bo--', label = 'Ch2')
	# plt.ylim([1000*y_min, 1000*y_max])
	plt.xlabel('I [A]')
	plt.ylabel('V [mV]')
	plt.savefig(dir_name + '\\' +'plot_IV_curve.pdf')
	# plt.show()
	plt.close()


	return time_array, I_shunt, Vsample_1, Vsample_2




#End IV curve
##########################################################################################




##########################################################################################
#Start IV curve fit

#fit to DC offset, linear resistance, Ic and n value
def curve_fit_IV(I_meas, V_meas, Ic_guess, V_criterion):

	#Voltage offset, linear resistance, Ic and n value
	bnds = ((-30e-3,30e-3), (1e-10,10e-3),(0.1*Ic_guess, 5*Ic_guess),(5,40))
	sol = differential_evolution(curve_fit_obj, bounds = bnds, args = (I_meas, V_meas, V_criterion), strategy='best1bin', maxiter=200, popsize=100, tol=1e-4, seed=False, mutation=(0, 0.2), recombination=0.4, disp=False, polish = True, init = 'random', updating = 'deferred', workers = 3)

	offset_fit = sol.x[0]
	resistance_fit = sol.x[1]
	Ic_fit = sol.x[2]
	n_fit = sol.x[3]

	print('\n')
	print('********************')
	print('Optimization convergence: ', sol.fun)
	print('Voltage offset [micro-V]: ', offset_fit)
	print('Resistance [micro-ohm]: ', resistance_fit)
	print('Critical current [Amps]: ', Ic_fit)
	print('n value [-]: ', n_fit)
	print('********************')
	print('\n')

	return offset_fit, resistance_fit, Ic_fit, n_fit




#Objective function to be called in curve fit optimizer
#fit DC offset, linear resistance and SC contribution
def curve_fit_obj(x, current, V_raw, V_criterion):

	V = x[0] + current*x[1] + V_criterion*(np.power(current/x[2],x[3]))
	
	nan_index = np.argwhere(current<0)
	V[nan_index] = 0
	V_raw[nan_index] = 0
	err_val = np.linalg.norm(V-V_raw)

	return err_val
		


#End IV curve fit
##########################################################################################







##########################################################################################
#Start cooldown monitor


def monitor_cooldown(rm):


	#Initialize instruments 
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage=3)

	#Initialize vectors to be filled in IV curve
	time_array = []
	Vsample_1 = []
	Vsample_2 = []

	#Create a figure that will be updated live
	fig = plt.figure(figsize=(8,6))
	ax1 = fig.add_subplot(1, 1, 1)
	plt.ion()
	L1, = ax1.plot(time_array, Vsample_1, 'k', label = 'Ch1')
	L2, = ax1.plot(time_array, Vsample_2, 'b', label = 'Ch2')
	
	#Start IV curve
	while True:

		#Get voltages from meters
		time_array.append(time.time())
		Vsample_1.append(get_nanovm(nanovm, ch_num = 1))
		Vsample_2.append(get_nanovm(nanovm, ch_num = 1))

		#Print values. Could be used to recover valuable data if program crashes
		print(i, time_array[i], I_shunt[i], Vsample_1[i], Vsample_2[i])

		L1.set_ydata(Vsample_1)
		L1.set_xdata(time_array)
		L2.set_ydata(Vsample_2)
		L2.set_xdata(time_array)

		plt.pause(0.01)
		time.sleep(1)
		plt.savefig(dir_name + '\\' +'cooldown.png', dpi=500) #Simply over-writes existing photo, for now

	plt.show()
	plt.close()

	return 


#End cooldown monitor
##########################################################################################



