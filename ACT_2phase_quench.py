


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


	# continuous_record()
	# ACT_IV_curve()
	# ramp_slow()

	# turn_psu_off()


	reed_test()
	return




def reed_test():

	dir_name = 'Results/2023_03_16_SBIR2Phase_500A_HEATER_save6'

	Vs_outerlayers = np.loadtxt(Path(dir_name + '/Vs_outerlayers.txt'))
	Vs_innerlayers = np.loadtxt(Path(dir_name + '/Vs_innerlayers.txt'))
	I_shunt = np.loadtxt(Path(dir_name + '/V_shunt.txt'))
	V_heater = np.loadtxt(Path(dir_name + '/V_heater.txt'))
	Vhall_ground_outerlayers = np.loadtxt(Path(dir_name + '/Vhall_ground_outerlayers.txt'))
	Vhall_ground_innerlayers = np.loadtxt(Path(dir_name + '/Vhall_ground_innerlayers.txt'))
	Vhall_pos_outerlayers = np.loadtxt(Path(dir_name + '/Vhall_pos_outerlayers.txt'))
	Vhall_pos_innerlayers = np.loadtxt(Path(dir_name + '/Vhall_pos_innerlayers.txt'))

	plt.figure()
	plt.plot(Vhall_ground_outerlayers - Vhall_ground_outerlayers[0])
	plt.plot(Vhall_ground_innerlayers - Vhall_ground_innerlayers[0])
	plt.plot(Vhall_pos_outerlayers - Vhall_pos_outerlayers[0])
	plt.plot(Vhall_pos_innerlayers - Vhall_pos_innerlayers[0])
	plt.show()



	return



def turn_psu_off():

	rm = visa.ResourceManager('@py')
	SSTF_psu = init_SSTF_psu(rm)
	set_SSTF_psu(SSTF_psu, 0)

	return




def ramp_slow():

	rm = visa.ResourceManager('@py')
	SSTF_psu = init_SSTF_psu(rm)

	I_end = 500
	I_inc = 5
	I_vec = np.arange(0, I_end + I_inc, I_inc)

	for i in np.arange(np.size(I_vec)):

		set_SSTF_psu(SSTF_psu, I_vec[i])
		time.sleep(0.25)


	return



def continuous_record():


	test_code = '2023_03_16_SBIR2Phase_500A_HEATER'
	dir_name = create_folder(test_code)

	time_acquire = 10
	fs = 1000 #sample frequency
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


	Vs_outerlayers = mod1_ai0
	Vs_innerlayers = mod1_ai1
	V_shunt = mod1_ai2
	V_heater = mod1_ai3

	Vhall_ground_outerlayers = mod2_ai0
	Vhall_ground_innerlayers = mod2_ai1
	Vhall_pos_outerlayers = mod2_ai2
	Vhall_pos_innerlayers = mod2_ai3

	I_shunt = -V_shunt/0.00002497


	np.savetxt(Path(dir_name + '/Vs_outerlayers.txt'), Vs_outerlayers)
	np.savetxt(Path(dir_name + '/Vs_innerlayers.txt'), Vs_innerlayers)
	np.savetxt(Path(dir_name + '/V_shunt.txt'), I_shunt)
	np.savetxt(Path(dir_name + '/V_heater.txt'), V_heater)
	np.savetxt(Path(dir_name + '/Vhall_ground_outerlayers.txt'), Vhall_ground_outerlayers)
	np.savetxt(Path(dir_name + '/Vhall_ground_innerlayers.txt'), Vhall_ground_innerlayers)
	np.savetxt(Path(dir_name + '/Vhall_pos_outerlayers.txt'), Vhall_pos_outerlayers)
	np.savetxt(Path(dir_name + '/Vhall_pos_innerlayers.txt'), Vhall_pos_innerlayers)

	plt.figure()
	ax1 = plt.subplot(2,1,1)
	ax2 = plt.subplot(2,1,2)
	

	ax1.plot(Vs_outerlayers, 'orange')
	ax1.plot(Vs_innerlayers, 'red')

	ax2.plot(Vhall_ground_outerlayers, 'k', label = 'Vhall_ground_outerlayers')
	ax2.plot(Vhall_ground_innerlayers, 'grey', label = 'Vhall_ground_innerlayers')
	ax2.plot(Vhall_pos_outerlayers, 'orange', label = 'Vhall_pos_outerlayers')
	ax2.plot(Vhall_pos_innerlayers, 'red', label = 'Vhall_pos_innerlayers')

	ax1.legend(frameon=False)
	ax2.legend(frameon=False)
	plt.show()
	plt.savefig(Path(dir_name + '/quench.pdf'))



	return 







def ACT_IV_curve():

	test_code = '2023_03_16_SBIR2Phase_protection_tests1'
	# test_code = 'delete'

	#Initialize power supply
	rm = visa.ResourceManager('@py')
	print(rm.list_resources())
	SSTF_psu = init_SSTF_psu(rm)

	#Ramp up and down
	# I_start = 0
	# I_end = 740 # 800
	# dI = 20 #WAS
	I_start = 0
	I_end = 500 # 800
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
	V_sample_max = 20/1000 #Disable PSU if voltage exceeds this
	t_settle = 1 #time to wait before recording voltage
	t_plot = 0.5 #time to plot
	t_record = 1 #time for NI dAQ to average

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
	
	Vs_outerlayers = np.zeros(num_points)
	Vs_innerlayers = np.zeros(num_points)
	I_shunt = np.zeros(num_points)
	V_heater = np.zeros(num_points)
	Vhall_ground_outerlayers = np.zeros(num_points)
	Vhall_ground_innerlayers = np.zeros(num_points)
	Vhall_pos_outerlayers = np.zeros(num_points)
	Vhall_pos_innerlayers = np.zeros(num_points)


	#Check starting point before telling power supply to ramp
	time_array[0] = time.time()

	Vs_outerlayers_i, Vs_innerlayers_i, I_shunt_i, V_heater_i, Vhall_ground_outerlayers_i, Vhall_ground_innerlayers_i, Vhall_pos_outerlayers_i, Vhall_pos_innerlayers_i  = get_cDAQ_8ch(t_record)


	Vs_outerlayers[0] = Vs_outerlayers_i
	Vs_innerlayers[0] = Vs_innerlayers_i
	I_shunt[0] = I_shunt_i
	V_heater[0] = V_heater_i
	Vhall_ground_outerlayers[0] = Vhall_ground_outerlayers_i
	Vhall_ground_innerlayers[0] = Vhall_ground_innerlayers_i
	Vhall_pos_outerlayers[0] = Vhall_pos_outerlayers_i
	Vhall_pos_innerlayers[0] = Vhall_pos_innerlayers_i

	plt.close('all')


	#Start IV curve UP
	for i in np.arange(num_points):

		set_SSTF_psu(SSTF_psu, I_vec[i]) #Set power supply to next current
	
		time.sleep(t_settle) # Dwell to eliminate inductive voltage

		#Get voltages from meters
		time_array[i] = time.time()

		Vs_outerlayers_i, Vs_innerlayers_i, I_shunt_i, V_heater_i, Vhall_ground_outerlayers_i, Vhall_ground_innerlayers_i, Vhall_pos_outerlayers_i, Vhall_pos_innerlayers_i  = get_cDAQ_8ch(t_record)

		Vs_outerlayers[i] = Vs_outerlayers_i
		Vs_innerlayers[i] = Vs_innerlayers_i
		I_shunt[i] = I_shunt_i
		V_heater[i] = V_heater_i
		Vhall_ground_outerlayers[i] = Vhall_ground_outerlayers_i
		Vhall_ground_innerlayers[i] = Vhall_ground_innerlayers_i
		Vhall_pos_outerlayers[i] = Vhall_pos_outerlayers_i
		Vhall_pos_innerlayers[i] = Vhall_pos_innerlayers_i


		print("Programed, measured current: ", I_vec[i], I_shunt[i])
		print('outer, inner layer voltage: ', Vs_outerlayers[i], Vs_innerlayers[i])


		np.savetxt(Path(dir_name + '/Vs_outerlayers.txt'), Vs_outerlayers)
		np.savetxt(Path(dir_name + '/Vs_innerlayers.txt'), Vs_innerlayers)
		np.savetxt(Path(dir_name + '/V_shunt.txt'), I_shunt)
		np.savetxt(Path(dir_name + '/V_heater.txt'), V_heater)
		np.savetxt(Path(dir_name + '/Vhall_ground_outerlayers.txt'), Vhall_ground_outerlayers)
		np.savetxt(Path(dir_name + '/Vhall_ground_innerlayers.txt'), Vhall_ground_innerlayers)
		np.savetxt(Path(dir_name + '/Vhall_pos_outerlayers.txt'), Vhall_pos_outerlayers)
		np.savetxt(Path(dir_name + '/Vhall_pos_innerlayers.txt'), Vhall_pos_innerlayers)



		#Plot curve, update y axis limits if needed
	
		fig = plt.figure(figsize=(8,6))
		ax1 = plt.subplot(2,1,1)
		ax2 = plt.subplot(2,1,2)

		ax1.plot(I_shunt[0:(i+1)], Vs_outerlayers[0:(i+1)], 'orange', label = 'Vs_outerlayers')
		ax1.plot(I_shunt[0:(i+1)], Vs_innerlayers[0:(i+1)], 'red', label = 'Vs_innerlayers')

		# ax2.plot(I_shunt[0:(i+1)], Vhall_ground_outerlayers[0:(i+1)]/Vhall_ground_innerlayers[0:(i+1)], 'k', label = 'Vhall_ground_ratio')
		# ax2.plot(I_shunt[0:(i+1)], Vhall_pos_outerlayers[0:(i+1)]/Vhall_pos_innerlayers[0:(i+1)], 'orange', label = 'Vhall_pos_ratio')

		ax2.plot(I_shunt[0:(i+1)], Vhall_ground_outerlayers[0:(i+1)], 'k', label = 'Vhall_ground_outerlayers')
		ax2.plot(I_shunt[0:(i+1)], Vhall_ground_innerlayers[0:(i+1)], 'grey', label = 'Vhall_ground_innerlayers')
		ax2.plot(I_shunt[0:(i+1)], Vhall_pos_outerlayers[0:(i+1)], 'orange', label = 'Vhall_pos_outerlayers')
		ax2.plot(I_shunt[0:(i+1)], Vhall_pos_innerlayers[0:(i+1)], 'red', label = 'Vhall_pos_innerlayers')

		ax1.set_xlabel('I [A]')
		ax2.set_xlabel('I [A]')		
		ax1.set_ylabel('V [V]')
		ax2.set_ylabel('V [V]')

		ax1.legend(frameon=False)
		ax2.legend(frameon=False)

		plt.show(block=False)
		plt.pause(t_plot)
		plt.close()



	fig = plt.figure(figsize=(8,6))
	ax1 = plt.subplot(2,1,1)
	ax2 = plt.subplot(2,1,2)

	ax1.plot(I_shunt[0:(i+1)], Vs_outerlayers[0:(i+1)], 'orange', label = 'Vs_outerlayers')
	ax1.plot(I_shunt[0:(i+1)], Vs_innerlayers[0:(i+1)], 'red', label = 'Vs_innerlayers')

	ax2.plot(I_shunt[0:(i+1)], Vhall_ground_outerlayers[0:(i+1)], 'k', label = 'Vhall_ground_outerlayers')
	ax2.plot(I_shunt[0:(i+1)], Vhall_ground_innerlayers[0:(i+1)], 'grey', label = 'Vhall_ground_innerlayers')
	ax2.plot(I_shunt[0:(i+1)], Vhall_pos_outerlayers[0:(i+1)], 'orange', label = 'Vhall_pos_outerlayers')
	ax2.plot(I_shunt[0:(i+1)], Vhall_pos_innerlayers[0:(i+1)], 'red', label = 'Vhall_pos_innerlayers')

	ax1.set_xlabel('I [A]')
	ax2.set_xlabel('I [A]')		
	ax1.set_ylabel('V [V]')
	ax2.set_ylabel('V [V]')

	ax1.legend(frameon=False)
	ax2.legend(frameon=False)
	plt.savefig(Path(dir_name + '/measurement_plot.pdf'))


	return dir_name





def plot_GA_curve():

	dir_name = 'Results/' + '2023_01_05_testramp_300A_save1'

	Vs_GA1 = np.loadtxt(Path(dir_name + '/Vs_GA1.txt'))
	Vs_GA2 = np.loadtxt(Path(dir_name + '/Vs_GA2.txt'))
	Vs_CORE = np.loadtxt(Path(dir_name + '/Vs_CORE.txt'))
	Vs_OUTER = np.loadtxt(Path(dir_name + '/Vs_OUTER.txt'))
	Vs_INNER = np.loadtxt(Path(dir_name + '/Vs_INNER.txt'))
	I_shunt = np.loadtxt(Path(dir_name + '/I_shunt.txt'))


	fig = plt.figure(figsize=(8,6))
	ax = plt.subplot(1,1,1)
	ax.plot(I_shunt, 1000*Vs_GA1, label = 'Vs_GA1')
	ax.plot(I_shunt, 1000*Vs_GA2, label = 'Vs_GA2')
	# ax.plot(I_shunt, 1000*Vs_CORE, label = 'Vs_CORE')
	# ax.plot(I_shunt, 1000*Vs_OUTER, label = 'Vs_OUTER')
	# ax.plot(I_shunt, 1000*Vs_INNER, label = 'Vs_INNER')
	plt.xlabel('I [A]')
	plt.ylabel('V [mV]')
	plt.legend(frameon=False)
	plt.show()

	#savefig(Path(dir_name + '/measurement_plot.pdf'))


	return



#Function for differentially measuring all 5 channels of ADS1262. Returns voltages in microvolts
def get_cDAQ_8ch(time_acquire):


	fs = 2000 #sample frequency
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



	Vs_outerlayers = np.mean(mod1_ai0)
	Vs_innerlayers = np.mean(mod1_ai1)
	V_shunt = np.mean(mod1_ai2)
	V_heater = np.mean(mod1_ai3)

	Vhall_ground_outerlayers = np.mean(mod2_ai0)
	Vhall_ground_innerlayers = np.mean(mod2_ai1)
	Vhall_pos_outerlayers = np.mean(mod2_ai2)
	Vhall_pos_innerlayers = np.mean(mod2_ai3)

	I_shunt = -V_shunt/0.00002497


	return Vs_outerlayers, Vs_innerlayers, I_shunt, V_heater, Vhall_ground_outerlayers, Vhall_ground_innerlayers, Vhall_pos_outerlayers, Vhall_pos_innerlayers






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



