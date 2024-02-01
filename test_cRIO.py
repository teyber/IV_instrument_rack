


import numpy as np
import matplotlib.pyplot as plt

import time




import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from nidaqmx import system

import nidaqmx.system


def main():

	# get_measurement()

	return








# def init_get_first_meas():
# 	fs = 1000
# 	samps_per_ch = 10
# 	try:
		
# 		with nidaqmx.Task() as task:	
# 			task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)

# 			task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, samps_per_chan=samps_per_ch) # you may not need samps_per_chan
# 			task.start()
# 			value = task.read(number_of_samples_per_channel=samps_per_ch, timeout=0.1)
# 			task.stop()
# 			print(value)

# 	except:
#  		print("An exception occurred")

	

# 	return




def get_measurement():

	fs = 25000 #sample frequency
	time_acquire = 1 #time to acquire data
	num_samples = int(fs*time_acquire)


	with nidaqmx.Task() as task:
		
		#Sample voltages and current shunt
		task.ai_channels.add_ai_voltage_chan(physical_channel="cRIO1/Mod1/ai0",max_val=0.5, min_val=-0.5)

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



