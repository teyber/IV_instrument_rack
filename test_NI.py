


import numpy as np
import matplotlib.pyplot as plt

import time




import nidaqmx
from nidaqmx import constants
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from nidaqmx import system


def main():

	fs = 100 #sample frequency
	time_acquire = 0.1 #time to acquire data
	num_samples = int(fs*time_acquire)


	with nidaqmx.Task() as task:
		
		#Sample voltages and current shunt
		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai0",max_val=0.5, min_val=-0.5)
		task.ai_channels.add_ai_voltage_chan(physical_channel="cDAQ1Mod1/ai1",max_val=0.5, min_val=-0.5)

		task.timing.cfg_samp_clk_timing(rate=fs, sample_mode=nidaqmx.constants.AcquisitionType.FINITE, samps_per_chan=num_samples) # you may not need samps_per_chan


		task.start()
		value = task.read(number_of_samples_per_channel=num_samples, timeout=10*time_acquire)
		task.stop()

	shunt_voltage = np.mean(np.asarray(value[0]))
	shunt_current_A = shunt_voltage/0.00002497

	return shunt_current_A










if __name__ == "__main__": main()



