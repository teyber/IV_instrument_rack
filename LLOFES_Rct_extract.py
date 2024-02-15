


import numpy as np
import matplotlib.pyplot as plt
import time
from pathlib import Path
import os

import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from nidaqmx import system

import pyvisa as visa



def main():

	LLOFES_IV_curve()

	# rm = visa.ResourceManager('@py')
	# print(rm.list_resources())
	# SSTF_psu = init_SSTF_psu(rm)
	# set_SSTF_psu(SSTF_psu, 0)

	return






def LLOFES_IV_curve():

	test_code = 'DELETE_2024_02_15_in-core_out-IL2_40A'	
		
	#Initialize power supply
	rm = visa.ResourceManager('@py')
	print(rm.list_resources())
	SSTF_psu = init_SSTF_psu(rm)

	#Ramp up and down
	I_start = 0
	I_end = 40 # 900 (probably try lower current for safety)
	dI = 5 #WAS

	#Ramp up and down
	dir_name_up = run_IV_curve(rm, SSTF_psu, I_start, I_end, dI, test_code) #ramp up
	time.sleep(0.1)
	dir_name_up = run_IV_curve(rm, SSTF_psu, I_end, I_start, -dI, test_code) #ramp down


	#plot data and extract resistance


	return







def run_IV_curve(rm, SSTF_psu, I_start, I_end, I_inc, test_code):

	#IV parameters
	I_vec = np.arange(I_start, I_end + I_inc, I_inc)
	t_settle = 1 #time to wait before recording voltage
	t_plot = 0.75 #time to plot
	t_record = 0.2 #time for NI dAQ to average

	#Create a folder for this result (see helper_functions)
	dir_name = create_folder(test_code)

	# Ask user to double check current range before proceeding
	print('------------ Safety check ------------')
	print('Programmed current range [A]: ', I_vec)
	print('0 - Exit')		
	print('1 - Energize systems')
	current_warning = int(input('Is this correct? '))
	
	if current_warning == 1: print('Continuing with IV curve - systems will be energized')
	else: return dir_name


	#Initialize vectors to be filled in IV curve
	num_points = np.size(I_vec)
	time_array = np.zeros(num_points)
	Vs = np.zeros(num_points)
	I_shunt = np.zeros(num_points)



	#Clear the error that happens with the CDAQ
	get_cDAQ_2ch(t_record, clear_init_error = True)


	#Check starting point before telling power supply to ramp
	time_array[0] = time.time()
	Vs_i, I_shunt_i = get_cDAQ_2ch(t_record, clear_init_error = False) 

	Vs[0] = Vs_i
	I_shunt[0] = I_shunt_i

	plt.close('all')


	#Start IV curve UP
	for i in np.arange(num_points):

		set_SSTF_psu(SSTF_psu, I_vec[i]) #Set power supply to next current
	
		time.sleep(t_settle) # Dwell to eliminate inductive voltage

		#Get voltages from meters
		time_array[i] = time.time()

		Vs_i, I_shunt_i, = get_cDAQ_2ch(t_record,  clear_init_error = False) 

		Vs[i] = Vs_i
		I_shunt[i] = I_shunt_i



		print("Programed, measured current: ", I_vec[i], I_shunt[i])
		print('Voltages: ', Vs_i)

		np.savetxt(Path(dir_name + '/time_array.txt'), time_array)	
		np.savetxt(Path(dir_name + '/I_vec.txt'), I_vec)	

		np.savetxt(Path(dir_name + '/Vs.txt'), Vs)
		

		#Plot curve, update y axis limits if needed
		fig = plt.figure(figsize=(8,6))
		ax1 = plt.subplot(1,1,1)

		ax1.plot(I_shunt[0:(i+1)], 1000*Vs[0:(i+1)], 'ko--')

		ax1.set_xlabel('I1 ONLY [A]')			
		ax1.set_ylabel('V$_{sample}$ [mV]')

		# if (I_vec[i]*2)<1410:
		# 	plt.show(block=False)
		# else:

		plt.show(block=False)

		plt.pause(t_plot)
		plt.close()



	fig = plt.figure(figsize=(8,6))
	ax = plt.subplot(1,1,1)
	ax.plot(I_shunt, 1000*Vs)
	plt.xlabel('I1 [A]')
	plt.ylabel('V [mV]')
	plt.legend(frameon=False)
	plt.savefig(Path(dir_name + '/measurement_plot.pdf'))


	return dir_name








#Function for differentially measuring all 5 channels of ADS1262. Returns voltages in microvolts
def get_cDAQ_2ch(time_acquire, clear_init_error):

	if clear_init_error == True:
		#Having a very strange error where the CDAQ / 9238 cards need to have the timing changed to not have an error
		#Previously did this manually in max

		fs = 1000
		samps_per_ch = 10
		try:
			with nidaqmx.Task() as task:	
				task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
				task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=samps_per_ch) # you may not need samps_per_chan
				task.start()
				value = task.read(number_of_samples_per_channel = samps_per_ch, timeout = 0.1)
				task.stop()
				print(value)

		except:
	 		print("An exception occurred")
	 	
		return

	else:
		#record as normal


		fs = 1000 #sample frequency
		num_samples = int(fs*time_acquire)

		with nidaqmx.Task() as task:
			
			#Sample voltages and current shunt
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai1",max_val=0.5, min_val=-0.5)

			task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan


			task.start()
			value = task.read(number_of_samples_per_channel=num_samples, timeout=2*time_acquire)
			task.stop()

			mod1_ai0 = np.asarray(value[0])
			mod1_ai1 = np.asarray(value[1])


	Vs = np.mean(mod1_ai0)
	V_shunt = np.mean(mod1_ai1)
	I_shunt = V_shunt/0.00002497

	return Vs, I_shunt




def init_SSTF_psu(rm):

	SSTF_psu =  rm.open_resource("TCPIP::169.254.58.10::gpib0,4::INSTR")	
	SSTF_psu.write_termination = '\n'
	SSTF_psu.read_termination = '\n'
	SSTF_psu.timeout = 1000
	SSTF_psu.write('*IDN?')
	time.sleep(0.1)
	print(SSTF_psu.read())

	print('NEW ANALOG CARD WITH NEW SLOPES')

	#Xiaorong Email
	# The new box, 4861B, is set to output a voltage between +/- 5 V. We also updated the VI configuration file with the following commands to communicate with 4861B. 
	# - B 4.999, set the offset to -0.001 V. This command, together with D 0, sends a control voltage of -0.001 V to the power supplies when the power supplies are expected to output 0 A. Command for 4861A: B 4.995. 
	# - M 1.0, set the slope to 1. Command for 4861A: M 0.5, which may indicate that the output range for 4861A was set to +/- 10 V.

	# The following commands remain the same as those for 4861A.
	# - D 0, set the output to 0 V during the initialization. 
	# - L 5, set the output limit to 5 V. 
	# More details on the commands for 4861b can be found here. 



	time.sleep(0.1)
	SSTF_psu.write('inst 1')
	time.sleep(0.1)
	# SSTF_psu.write('b4.995')
	SSTF_psu.write('b4.999')
	time.sleep(0.1)
	# SSTF_psu.write('m0.5')
	SSTF_psu.write('m1.0')
	time.sleep(0.1)
	SSTF_psu.write('l5')
	time.sleep(0.1)
	SSTF_psu.write('d0')
	time.sleep(0.1)

	return SSTF_psu





def set_SSTF_psu(SSTF_psu, I_psu):

	V_cmd = I_psu*(5/1000) #Volts to power supply

	SSTF_psu.write('D ' + str(V_cmd))
	time.sleep(0.1)	

	return




def create_folder(test_code_0):
	#Create a folder for the test, make sure we do not overwrite any prior tests
	#Append a number to the requested file name

	keep_trying = True
	code_num = 1
	dir_name = 'Results/'+test_code_0+'_save' + str(code_num)
	while keep_trying == True:
		dir_name = 'Results/'+ test_code_0 + '_save' + str(code_num)
		if os.path.exists(dir_name) and code_num < 10000:
			code_num += 1
		else:
			os.makedirs(dir_name)
			keep_trying = False

	print('Saving results to directory: ', dir_name)
	return dir_name





if __name__ == "__main__": main()



