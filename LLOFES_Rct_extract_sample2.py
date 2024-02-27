


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

	test_code = '2024_02_27_40A_neg-IL2_pos-OL1'	
		
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
	L0_T0 = np.zeros(num_points)
	L0_T1 = np.zeros(num_points)
	L0_T2 = np.zeros(num_points)
	L1_T0 = np.zeros(num_points)
	L1_T1 = np.zeros(num_points)
	L1_T2 = np.zeros(num_points)
	L2_T0 = np.zeros(num_points)
	L2_T1 = np.zeros(num_points)
	L2_T2 = np.zeros(num_points)
	L3_T0 = np.zeros(num_points)
	L3_T1 = np.zeros(num_points)
	L3_T2 = np.zeros(num_points)
	L4_T0_CORE = np.zeros(num_points)
	I_shunt = np.zeros(num_points)


	#Clear the error that happens with the CDAQ
	get_cDAQ_14ch(t_record, clear_init_error = True)


	#Check starting point before telling power supply to ramp
	time_array[0] = time.time()
	I_shunt_i, L0_T0_i, L0_T1_i, L0_T2_i, L1_T0_i, L1_T1_i, L1_T2_i, L2_T0_i, L2_T1_i, L2_T2_i, L3_T0_i, L3_T1_i, L3_T2_i, L4_T0_CORE_i = get_cDAQ_14ch(t_record, clear_init_error = False) 


	L0_T0[0] = L0_T0_i
	L0_T1[0] = L0_T1_i
	L0_T2[0] = L0_T2_i
	L1_T0[0] = L1_T0_i
	L1_T1[0] = L1_T1_i
	L1_T2[0] = L1_T2_i
	L2_T0[0] = L2_T0_i
	L2_T1[0] = L2_T1_i
	L2_T2[0] = L2_T2_i
	L3_T0[0] = L3_T0_i
	L3_T1[0] = L3_T1_i
	L3_T2[0] = L3_T2_i
	L4_T0_CORE[0] = L4_T0_CORE_i
	I_shunt[0] = I_shunt_i


	Vs[0] = Vs_i
	I_shunt[0] = I_shunt_i

	plt.close('all')


	#Start IV curve UP
	for i in np.arange(num_points):

		set_SSTF_psu(SSTF_psu, I_vec[i]) #Set power supply to next current
	
		time.sleep(t_settle) # Dwell to eliminate inductive voltage

		#Get voltages from meters
		time_array[i] = time.time()

		I_shunt_i, L0_T0_i, L0_T1_i, L0_T2_i, L1_T0_i, L1_T1_i, L1_T2_i, L2_T0_i, L2_T1_i, L2_T2_i, L3_T0_i, L3_T1_i, L3_T2_i, L4_T0_CORE_i = get_cDAQ_14ch(t_record, clear_init_error = False) 

		L0_T0[i] = L0_T0_i
		L0_T1[i] = L0_T1_i
		L0_T2[i] = L0_T2_i
		L1_T0[i] = L1_T0_i
		L1_T1[i] = L1_T1_i
		L1_T2[i] = L1_T2_i
		L2_T0[i] = L2_T0_i
		L2_T1[i] = L2_T1_i
		L2_T2[i] = L2_T2_i
		L3_T0[i] = L3_T0_i
		L3_T1[i] = L3_T1_i
		L3_T2[i] = L3_T2_i
		L4_T0_CORE[i] = L4_T0_CORE_i
		I_shunt[i] = I_shunt_i

		print("Programed, measured current: ", I_vec[i], I_shunt[i])

		np.savetxt(Path(dir_name + '/time_array.txt'), time_array)	
		np.savetxt(Path(dir_name + '/I_vec.txt'), I_vec)	

		np.savetxt(Path(dir_name + '/L0_T0.txt'), L0_T0)	
		np.savetxt(Path(dir_name + '/L0_T1.txt'), L0_T1)	
		np.savetxt(Path(dir_name + '/L0_T2.txt'), L0_T2)

		np.savetxt(Path(dir_name + '/L1_T0.txt'), L1_T0)	
		np.savetxt(Path(dir_name + '/L1_T1.txt'), L1_T1)	
		np.savetxt(Path(dir_name + '/L1_T2.txt'), L1_T2)

		np.savetxt(Path(dir_name + '/L2_T0.txt'), L2_T0)	
		np.savetxt(Path(dir_name + '/L2_T1.txt'), L2_T1)	
		np.savetxt(Path(dir_name + '/L2_T2.txt'), L2_T2)

		np.savetxt(Path(dir_name + '/L3_T0.txt'), L3_T0)	
		np.savetxt(Path(dir_name + '/L3_T1.txt'), L3_T1)	
		np.savetxt(Path(dir_name + '/L3_T2.txt'), L3_T2)

		

		#Plot curve, update y axis limits if needed
		plot_color = plt.cm.jet(np.linspace(0.1,0.9, 12))
		fig = plt.figure(figsize=(8,6))
		ax1 = plt.subplot(1,1,1)

		ax1.plot(I_shunt[0:(i+1)], 1000*L0_T0[0:(i+1)], color=plot_color[0])
		ax1.plot(I_shunt[0:(i+1)], 1000*L0_T1[0:(i+1)], color=plot_color[1])
		ax1.plot(I_shunt[0:(i+1)], 1000*L0_T2[0:(i+1)], color=plot_color[2])

		ax1.plot(I_shunt[0:(i+1)], 1000*L1_T0[0:(i+1)], color=plot_color[3])
		ax1.plot(I_shunt[0:(i+1)], 1000*L1_T1[0:(i+1)], color=plot_color[4])
		ax1.plot(I_shunt[0:(i+1)], 1000*L1_T2[0:(i+1)], color=plot_color[5])

		ax1.plot(I_shunt[0:(i+1)], 1000*L2_T0[0:(i+1)], color=plot_color[6])
		ax1.plot(I_shunt[0:(i+1)], 1000*L2_T1[0:(i+1)], color=plot_color[7])
		ax1.plot(I_shunt[0:(i+1)], 1000*L2_T2[0:(i+1)], color=plot_color[8])

		ax1.plot(I_shunt[0:(i+1)], 1000*L3_T0[0:(i+1)], color=plot_color[9])
		ax1.plot(I_shunt[0:(i+1)], 1000*L3_T1[0:(i+1)], color=plot_color[10])
		ax1.plot(I_shunt[0:(i+1)], 1000*L3_T2[0:(i+1)], color=plot_color[11])

		ax1.plot(I_shunt[0:(i+1)], 1000*L4_T_CORE[0:(i+1)], color=plot_color[12])


		ax1.set_xlabel('I1 [A]')			
		ax1.set_ylabel('V$_{sample}$ [mV]')

		plt.show(block=False)

		plt.pause(t_plot)
		plt.close()


	return dir_name








#Function for differentially measuring all 5 channels of ADS1262. Returns voltages in microvolts
def get_cDAQ_14ch(time_acquire, clear_init_error):

	if clear_init_error == True:
		#Having a very strange error where the CDAQ / 9238 cards need to have the timing changed to not have an error
		#Previously did this manually in max

		fs = 500
		samps_per_ch = 10
		try:
			with nidaqmx.Task() as task:	
				task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
				task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=samps_per_ch) # you may not need samps_per_chan
				task.start()
				value = task.read(number_of_samples_per_channel = samps_per_ch, timeout = 0.5)
				task.stop()
				print(value)

		except:
	 		print("An exception occurred")
	 	
		return

	else:
		#record as normal


		fs = 500 #sample frequency
		num_samples = int(fs*time_acquire)

		with nidaqmx.Task() as task:
			
			#Sample voltages and current shunt
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai1",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai2",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai3",max_val=0.5, min_val=-0.5)

			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod2/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod2/ai1",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod2/ai2",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod2/ai3",max_val=0.5, min_val=-0.5)

			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai1",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai2",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai3",max_val=0.5, min_val=-0.5)

			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai1",max_val=0.5, min_val=-0.5)


			task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan


			task.start()
			value = task.read(number_of_samples_per_channel=num_samples, timeout=2*time_acquire)
			task.stop()

			mod1_ai0 = np.asarray(value[0])
			mod1_ai1 = np.asarray(value[1])
			mod1_ai2 = np.asarray(value[2])
			mod1_ai3 = np.asarray(value[3])

			mod2_ai0 = np.asarray(value[4])
			mod2_ai1 = np.asarray(value[5])
			mod2_ai2 = np.asarray(value[6])
			mod2_ai3 = np.asarray(value[7])

			mod3_ai0 = np.asarray(value[8])
			mod3_ai1 = np.asarray(value[9])
			mod3_ai2 = np.asarray(value[10])
			mod3_ai3 = np.asarray(value[11])

			mod4_ai0 = np.asarray(value[12])
			mod4_ai1 = np.asarray(value[13])
			# mod4_ai2 = np.asarray(value[14])
			# mod4_ai3 = np.asarray(value[15])

	L0_T0 = np.mean(mod1_ai0)
	L0_T1 = np.mean(mod1_ai1)
	L0_T2 = np.mean(mod1_ai2)
	L1_T0 = np.mean(mod1_ai3)

	L1_T1 = np.mean(mod2_ai0)
	L1_T2 = np.mean(mod2_ai1)
	L2_T0 = np.mean(mod2_ai2)
	L2_T1 = np.mean(mod2_ai3)

	L2_T2 = np.mean(mod3_ai0)
	L3_T0 = np.mean(mod3_ai1)
	L3_T1 = np.mean(mod3_ai2)
	L3_T2 = np.mean(mod3_ai3)

	L4_T0_CORE = np.mean(mod4_ai0)
	V_shunt = np.mean(mod4_ai1)

	I_shunt = V_shunt/0.00002497

	return I_shunt, L0_T0, L0_T1, L0_T2, L1_T0, L1_T1, L1_T2, L2_T0, L2_T1, L2_T2, L3_T0, L3_T1, L3_T2, L4_T0_CORE




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


