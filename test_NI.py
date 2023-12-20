


import numpy as np
import matplotlib.pyplot as plt

import time




import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from nidaqmx import system


def main():

	get_cDAQ_16ch(time_acquire=1, clear_init_error=True)
	
	for i in np.arange(20):
		Vs_GA1, Vs_GA2, Vs_CORE, Vs_OUTER, Vs_INNER, I_shunt = get_cDAQ_16ch(time_acquire=1, clear_init_error=False)



	return





#Function for differentially measuring all 5 channels of ADS1262. Returns voltages in microvolts
def get_cDAQ_16ch(time_acquire, clear_init_error):

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

	else:
		#record as normal


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

			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai1",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai2",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod3/ai3",max_val=0.5, min_val=-0.5)

			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai0",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai1",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai2",max_val=0.5, min_val=-0.5)
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod4/ai3",max_val=0.5, min_val=-0.5)

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
			mod4_ai2 = np.asarray(value[14])
			mod4_ai3 = np.asarray(value[15])

		plt.figure()
		plt.plot(mod1_ai0)
		plt.show()

		Vs_GA1 = np.mean(mod1_ai0)
		Vs_GA2 = np.mean(mod1_ai1)
		Vs_CORE = np.mean(mod1_ai2)
		Vs_OUTER = np.mean(mod1_ai3)

		Vs_INNER = np.mean(mod2_ai0)
		V_shunt = np.mean(mod2_ai1)
		I_shunt = V_shunt/0.00002497

		return Vs_GA1, Vs_GA2, Vs_CORE, Vs_OUTER, Vs_INNER, I_shunt













def init_get_first_meas():
	fs = 1000
	samps_per_ch = 10
	try:
		
		with nidaqmx.Task() as task:	
			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)

			task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=samps_per_ch) # you may not need samps_per_chan
			task.start()
			value = task.read(number_of_samples_per_channel=samps_per_ch, timeout=0.1)
			task.stop()
			print(value)

	except:
 		print("An exception occurred")

	

	return




def get_measurement():

	fs = 25000 #sample frequency
	time_acquire = 1 #time to acquire data
	num_samples = int(fs*time_acquire)


	with nidaqmx.Task() as task:
		
		#Sample voltages and current shunt
		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai1",max_val=0.5, min_val=-0.5)

		task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan


		task.start()
		value = task.read(number_of_samples_per_channel=num_samples, timeout=(1.5*time_acquire+0.1))
		task.stop()

	time.sleep(0.5)
	mod1_ai0 = np.asarray(value[0])
	

	plt.figure()
	plt.plot(mod1_ai0)
	plt.show()

	return





# def get_stream():

# 	fs = 1000 #sample frequency
# 	time_acquire = 0.1 #time to acquire data
# 	num_samples = int(fs*time_acquire)

# 	with nidaqmx.Task() as task:
		
# 		#Sample voltages and current shunt
# 		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
# 		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai1",max_val=0.5, min_val=-0.5)

# 		time.sleep(0.1)

# 		# task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan


# 		task.timing.cfg_samp_clk_timing(rate=fs, source="OnboardClock", sample_mode=nidaqmx.constants.AcquisitionType.HW_TIMED_SINGLE_POINT) # you may not need samps_per_chan

		
# 		# task.timing.cfg_samp_clk_timing(rate=fs, source="OnboardClock", sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan
# 		time.sleep(0.1)

# 		# task.start()
# 		# value = task.read(number_of_samples_per_channel=num_samples, timeout=10*time_acquire)
# 		value = task.read()		
# 		# task.stop()

# 	mod1_ai0 = np.asarray(value[0])
	

# 	return













if __name__ == "__main__": main()



