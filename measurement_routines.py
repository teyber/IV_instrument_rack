


# import serial
import os
import time
import visa
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution


some_constant = 3


##########################################################################################
#IC curve

def run_IV_curve(I_start, I_end, I_inc, test_code = 'test_tape'):


	#IV parameters
	V_sample_max = 1e-3 #Disable PSU if voltage exceeds this
	t_dwell = 0.2 #200 milliseconds



	#Initialize instruments
	rm = visa.ResourceManager()
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage=3)


	# #Create folder if it doesn't exist
	# dir_name = 'Results\\' + test_code
	# if os.path.exists(dir_name):
	# 	print('Folder with test name already exists')
	# 	print('0 - return to main loop')		
	# 	print('1 - Continue')
	# 	folder_warning = input('What would you like to do?')

	# 	if folder_conflict == 1: 
	# 		continue
	# 	else: return

	# else:
	# 	os.makedirs(dir_name)


	# #Ask user to double check current range before proceeding
	# I_vec = np.arange(I_start, I_end + I_inc, I_inc)
	# print('Safety check')
	# print('Programmed current range [A]: ', np.min(I_vec), np.max(I_vec))
	# print('Programmed voltage threshold [V]: ', V_sample_max)
	# print('\n')
	# print('0 - return to main loop')		
	# print('1 - Continue with IV curve')
	# current_warning = input('What would you like to do?')

	# if current_warning == 1: 
	# 	print('Continuing with IV curve - systems will be energized')
	# 	continue

	# else: return

	#Initialize vectors to be filled in IV curve
	num_points = np.size(I_vec)
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

	ax1.set_xlim([x_min, x_max])
	ax1.set_ylim([y_min, y_max])
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

		#Plot curve, update y axis limits if needed
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
	plt.savefig(dir_name + '\\' +'plot_IV_curve.pdf')
	plt.close()


	#Ramp down, do not collect voltages along way
	time.sleep(0.1)
	down_ramp_time = 3
	print('IV curve complete. Beginning ramp down for ' + str(down_ramp_time) + ' seconds')
	ramp_sorenson_psu(sorenson_psu, I_ramp_time=down_ramp_time, I_ramp_mag=0)
	time.sleep(down_ramp_time+1)
	modify_sorenson_limits(sorenson_psu, max_I=0, max_V=0)


#Analye IV curve with curve fit
	print('Ch1 analysis')
	offset_ch1, resistance_ch1, Ic_ch1, n_ch1 = curve_fit_IV(I_shunt, Vsample_1, Ic_guess=1000, V_criterion=1e-6)
	
	print('Ch2 analysis')
	offset_ch2, resistance_ch2, Ic_ch2, n_ch2 = curve_fit_IV(I_shunt, Vsample_2, Ic_guess=1000, V_criterion=1e-6)


	#save output
	code_num = 1
	if os.path.exists(dir_name + '\\' + 'IV_curve_' + str(code_num)):
		code_num += 1
	else:
		np.savetxt(dir_name + '\\' +'IV_curve_' + str(code_num) + '.txt', np.vstack((time_array, I_shunt, Vsample_1, Vsample_2)))	
		np.savetxt(dir_name + '\\' +'ch1_fit_' + str(code_num) + '.txt', [offset_ch1, resistance_ch1, Ic_ch1, n_ch1])	
		np.savetxt(dir_name + '\\' +'ch2_fit_' + str(code_num) + '.txt', [offset_ch2, resistance_ch2, Ic_ch2, n_ch2])	



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


def monitor_cooldown():


	#Initialize instruments
	rm = visa.ResourceManager()
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




