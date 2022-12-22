


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

	GA_IV_curve()
	
	return






def GA_IV_curve():

	test_code = 'debug_21_12_2022'

	#Initialize power supply
	rm = visa.ResourceManager('@py')
	print(rm.list_resources())
	SSTF_psu = init_SSTF_psu(rm)

	#Ramp up and down
	I_start = 0
	I_end = 100
	dI = 10
	

	#Ramp up and down
	dir_name_up = run_IV_curve(rm, SSTF_psu, I_start, I_end, dI, test_code) #ramp up
	time.sleep(0.1)
	dir_name_up = run_IV_curve(rm, SSTF_psu, I_end, I_start, -dI, test_code) #ramp down


	#plot data and extract resistance


	return






def run_IV_curve(rm, SSTF_psu, I_start, I_end, I_inc, test_code):

	#IV parameters
	I_vec = np.arange(I_start, I_end + I_inc, I_inc)
	V_sample_max = 10/1000 #Disable PSU if voltage exceeds this
	t_settle = 0.5 #time to wait before recording voltage
	t_plot = 0.5 #time to plot
	t_record = 0.5 #time for NI dAQ to average

	#Create a folder for this result (see helper_functions)
	dir_name = create_folder(test_code)

	# Ask user to double check current range before proceeding
	print('------------ Safety check ------------')
	print('Programmed current range [A]: ', I_vec)
	print('Programmed voltage threshold [V], settle time [s]: ', V_sample_max, t_settle)
	print('0 - Exit')		
	print('1 - Energize systems')
	current_warning = int(input('Is this correct? '))
	
	if current_warning == 1: 
		print('Continuing with IV curve - systems will be energized')
	else: 
		return dir_name



	#Initialize vectors to be filled in IV curve
	num_points = np.size(I_vec)
	time_array = np.zeros(num_points)
	I_shunt = np.zeros(num_points)
	Vs_1 = np.zeros(num_points)
	Vs_2 = np.zeros(num_points)
	Vs_3 = np.zeros(num_points)
	Vs_4 = np.zeros(num_points)
	Vs_5 = np.zeros(num_points)
	Vs_6 = np.zeros(num_points)
	Vs_7 = np.zeros(num_points)


	#Check starting point before telling power supply to ramp
	time_array[0] = time.time()
	I_shunt_init, Vs_1_init, Vs_2_init, Vs_3_init, Vs_4_init, Vs_5_init, Vs_6_init, Vs_7_init = get_cDAQ_8ch(t_record)

	I_shunt[0] = I_shunt_init
	Vs_1[0] = Vs_1_init
	Vs_2[0] = Vs_2_init
	Vs_3[0] = Vs_3_init
	Vs_4[0] = Vs_4_init
	Vs_5[0] = Vs_5_init
	Vs_6[0] = Vs_6_init
	Vs_7[0] = Vs_7_init


	plt.close('all')


	#Start IV curve UP
	for i in np.arange(num_points):

		set_SSTF_psu(SSTF_psu, I_vec[i]) #Set power supply to next current
	
		time.sleep(t_settle) # Dwell to eliminate inductive voltage

		#Get voltages from meters
		time_array[i] = time.time()

		I_shunt_i, Vs_1_i, Vs_2_i, Vs_3_i, Vs_4_i, Vs_5_i, Vs_6_i, Vs_7_i = get_cDAQ_8ch(t_record)
		I_shunt[i] = I_shunt_init
		Vs_1[i] = Vs_1_i
		Vs_2[i] = Vs_2_i
		Vs_3[i] = Vs_3_i
		Vs_4[i] = Vs_4_i
		Vs_5[i] = Vs_5_i
		Vs_6[i] = Vs_6_i
		Vs_7[i] = Vs_7_i

		print("Programed, measured current: ", I_vec[i], I_shunt[i])
		print('Voltages: ', Vs_1_i, Vs_2_i, Vs_3_i, Vs_4_i, Vs_5_i, Vs_6_i, Vs_7_i)

		np.savetxt(Path(dir_name + '/time_array.txt'), time_array)	
		np.savetxt(Path(dir_name + '/I_vec.txt'), I_vec)		
		np.savetxt(Path(dir_name + '/I_shunt.txt'), I_shunt)
		np.savetxt(Path(dir_name + '/Vs_1.txt'), Vs_1)
		np.savetxt(Path(dir_name + '/Vs_2.txt'), Vs_2)
		np.savetxt(Path(dir_name + '/Vs_3.txt'), Vs_3)
		np.savetxt(Path(dir_name + '/Vs_4.txt'), Vs_4)
		np.savetxt(Path(dir_name + '/Vs_5.txt'), Vs_5)
		np.savetxt(Path(dir_name + '/Vs_6.txt'), Vs_6)
		np.savetxt(Path(dir_name + '/Vs_7.txt'), Vs_7)



		#Plot curve, update y axis limits if needed
	
		fig = plt.figure(figsize=(8,6))
		ax = plt.subplot(1,1,1)
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_1[0:(i+1)], 'ko--', label = 'Vs_1')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_2[0:(i+1)], 'ro--', label = 'Vs_2')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_3[0:(i+1)], label = 'Vs_3')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_4[0:(i+1)], label = 'Vs_4')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_5[0:(i+1)], label = 'Vs_5')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_6[0:(i+1)], label = 'Vs_6')
		ax.plot(I_shunt[0:(i+1)], 1000*Vs_7[0:(i+1)], label = 'Vs_7')

		plt.xlabel('I [A]')
		plt.ylabel('V [mV]')
		plt.legend(frameon=False)
		plt.show(block=False)
		plt.pause(t_plot)
		plt.close()



	fig = plt.figure(figsize=(8,6))
	ax = plt.subplot(1,1,1)
	ax.plot(I_shunt, 1000*Vs_1, label = 'Vs_1')
	ax.plot(I_shunt, 1000*Vs_2, label = 'Vs_2')
	ax.plot(I_shunt, 1000*Vs_3, label = 'Vs_3')
	ax.plot(I_shunt, 1000*Vs_4, label = 'Vs_4')
	ax.plot(I_shunt, 1000*Vs_5, label = 'Vs_5')
	ax.plot(I_shunt, 1000*Vs_6, label = 'Vs_6')
	ax.plot(I_shunt, 1000*Vs_7, label = 'Vs_7')
	plt.xlabel('I [A]')
	plt.ylabel('V [mV]')
	plt.legend(frameon=False)
	plt.savefig(Path(dir_name + '/measurement_plot.pdf'))


	return dir_name









#Function for differentially measuring all 5 channels of ADS1262. Returns voltages in microvolts
def get_cDAQ_8ch(time_acquire):


	fs = 5000 #sample frequency
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

	V_shunt = np.mean(mod1_ai0)
	I_shunt = V_shunt/0.00002497

	Vs_1 = np.mean(mod1_ai1)
	Vs_2 = np.mean(mod1_ai2)
	Vs_3 = np.mean(mod1_ai3)

	Vs_4 = np.mean(mod2_ai0)
	Vs_5 = np.mean(mod2_ai1)
	Vs_6 = np.mean(mod2_ai2)
	Vs_7 = np.mean(mod2_ai3)

	return I_shunt, Vs_1, Vs_2, Vs_3, Vs_4, Vs_5, Vs_6, Vs_7







def init_SSTF_psu(rm):

	SSTF_psu =  rm.open_resource("TCPIP::169.254.58.10::gpib0,4::INSTR")	
	SSTF_psu.write_termination = '\n'
	SSTF_psu.read_termination = '\n'
	SSTF_psu.timeout = 1000
	SSTF_psu.write('*IDN?')
	time.sleep(0.1)
	print(SSTF_psu.read())

	time.sleep(0.1)
	SSTF_psu.write('inst 1')
	time.sleep(0.1)
	SSTF_psu.write('b4.995')
	time.sleep(0.1)
	SSTF_psu.write('m0.5')
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



