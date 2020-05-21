


import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok

import os
import time


# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}


#USER INPUT HERE: ADC range #Ranges: "PS4000_10MV", "PS4000_20MV", "PS4000_50MV", "PS4000_100MV", "PS4000_200MV", "PS4000_500MV", "PS4000_1V",  "PS4000_2V",
chRange = 1

#USER INPUT HERE: sampling frequency, recording time

meas_channels = [2,3,7]

sample_period_microseconds = 5 #5 microseconds between measurements (200 kHz)
sizeOfOneBuffer = int(0.2e6) #capture 1 second at 200 KHz
numBuffersToCapture = int(1) #record data for 2 seconds. Code should work for up to 20*60 seconds at 200 kHz


#Items below need to be globally scoped
totalSamples = sizeOfOneBuffer * numBuffersToCapture
nextSample = 0 


if (0 in meas_channels):
	bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferAMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (1 in meas_channels):
	bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferBMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (2 in meas_channels):
	bufferCompleteC = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferCMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (3 in meas_channels):
	bufferCompleteD = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferDMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (4 in meas_channels):
	bufferCompleteE = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferEMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (5 in meas_channels):
	bufferCompleteF = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferFMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (6 in meas_channels):
	bufferCompleteG = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferGMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)

if (7 in meas_channels):
	bufferCompleteH = np.zeros(shape=totalSamples, dtype=np.int16)
	bufferHMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)





def main():

	tot_start_time = time.time()

###########################################
#Prepare a results folder
	test_name = 'reed_may20_A01'
	dir_name = create_folder(test_name)


###########################################
#Record PICOSCOPE data
	stream_picoscope(dir_name)
	print('Streaming and saving time: ', np.round((time.time() - tot_start_time)/60, 1))	

###########################################
#Plot results (warning - will crash if arrays are huge)
	plot_start_time = time.time()
	plot_pico(dir_name, 0, 0) #plot entire length, for now
	print('Plotting time: ', np.round((time.time() - plot_start_time)/60, 1))	


	#If you want to look at a result that already exists, enter the directory here and comment out the above results
	# plot_pico('Results\\reed_may18_A01_save27', 0, 0.01) #20 minute acquisition


	print('Elapsed time: ', np.round((time.time() - tot_start_time)/60, 2))	

	return




def create_folder(test_code_0):
	#Create a folder for the test, make sure we do not overwrite any prior tests
	#Append a number to the requested file name

	keep_trying = True
	code_num = 1
	dir_name = 'Results\\'+test_code_0+'_save' + str(code_num)
	while keep_trying == True:
		dir_name = 'Results\\'+ test_code_0 + '_save' + str(code_num)
		if os.path.exists(dir_name) and code_num < 10000:
			code_num += 1
		else:
			os.makedirs(dir_name)
			keep_trying = False

	print('Saving results to directory: ', dir_name)
	return dir_name




def stream_picoscope(dir_name):

##################################################################
# Step 1. Open the oscilloscope using ps4000aOpenUnit(). 
##################################################################

	status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)

	try: assert_pico_ok(status["openunit"])
	except:
		powerStatus = status["openunit"]
		if powerStatus == 286: status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
		else:raise
		assert_pico_ok(status["changePowerSource"])


##################################################################
# Step 2. Select channels, ranges and AC/DC coupling using ps4000aSetChannel(). 
##################################################################

	#Arguments: handle, channel, enabled, COUPLING type,  range, analogOffset 	# handle = chandle, channel = PS4000a_CHANNEL_A = 0, enabled = 1,# coupling type = PS4000a_DC = 1,# range = PS4000a_2V = 7,# analogOffset = 0 V
	if (0 in meas_channels):
		status["setChA"] = ps.ps4000aSetChannel(chandle, 0, 1, 1, chRange, 0)
		assert_pico_ok(status["setChA"])

	if (1 in meas_channels):
		status["setChB"] = ps.ps4000aSetChannel(chandle, 1, 1, 1, chRange, 0)
		assert_pico_ok(status["setChB"])

	if (2 in meas_channels):
		status["setChC"] = ps.ps4000aSetChannel(chandle, 2, 1, 1, chRange, 0)
		assert_pico_ok(status["setChC"])

	if (3 in meas_channels):
		status["setChD"] = ps.ps4000aSetChannel(chandle, 3, 1, 1, chRange, 0)
		assert_pico_ok(status["setChD"])

	if (4 in meas_channels):
		status["setChE"] = ps.ps4000aSetChannel(chandle, 4, 1, 1, chRange, 0)
		assert_pico_ok(status["setChE"])

	if (5 in meas_channels):
		status["setChF"] = ps.ps4000aSetChannel(chandle, 5, 1, 1, chRange, 0)
		assert_pico_ok(status["setChF"])

	if (6 in meas_channels):
		status["setChG"] = ps.ps4000aSetChannel(chandle, 6, 1, 1, chRange, 0)
		assert_pico_ok(status["setChG"])

	if (7 in meas_channels):
		status["setChH"] = ps.ps4000aSetChannel(chandle, 7, 1, 1, chRange, 0)
		assert_pico_ok(status["setChH"])



##################################################################
# Step 3. Use the trigger setup functions [1] [2] [3] [4] to set up the trigger if required. 
##################################################################

	#Trigger arguments: handle, enable, source, threshold, direction, delay, autoTrigger_ms
	status["trigger"] = ps.ps4000aSetSimpleTrigger(chandle, 1, 0, 1024, 2, 0, 1) #was 100 ms autotrigger_ms
	assert_pico_ok(status["trigger"])


##################################################################
# Step 4. Call ps4000aSetDataBuffer() to tell the driver where your data buffer is. 
##################################################################

	memory_segment = 0 #?

	if (0 in meas_channels):
		status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'], bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersA"])

	if (1 in meas_channels):
		status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'], bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersB"])

	if (2 in meas_channels):
		status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'], bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersC"])

	if (3 in meas_channels):
		status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'], bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersD"])

	if (4 in meas_channels):
		status["setDataBuffersE"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_E'], bufferEMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersE"])

	if (5 in meas_channels):
		status["setDataBuffersF"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_F'], bufferFMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersF"])

	if (6 in meas_channels):
		status["setDataBuffersG"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_G'], bufferGMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersG"])

	if (7 in meas_channels):
		status["setDataBuffersH"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_H'], bufferHMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
		assert_pico_ok(status["setDataBuffersH"])



##################################################################
# Step 5. Set up downsampling and start the oscilloscope running using ps4000aRunStreaming(). 
##################################################################

	# sampleInterval = ctypes.c_int32(sample_period_microseconds)
	sampleInterval = ctypes.c_int16(sample_period_microseconds)	
	sampleUnits = ps.PS4000A_TIME_UNITS['PS4000A_US']
	maxPreTriggerSamples = 0 # We are not triggering:
	autoStopOn = 1
	downsampleRatio = 1	# No downsampling:
	status["runStreaming"] = ps.ps4000aRunStreaming(chandle, ctypes.byref(sampleInterval), sampleUnits, maxPreTriggerSamples, totalSamples, autoStopOn, downsampleRatio, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'], sizeOfOneBuffer)
	assert_pico_ok(status["runStreaming"])

	actualSampleInterval = sampleInterval.value

##################################################################
# Step 6. Call ps4000aGetStreamingLatestValues() to get data. 
##################################################################

	autoStopOuter = False
	wasCalledBack = False

	cFuncPtr = ps.StreamingReadyType(pico_streaming_callback) 	# Convert the python function into a C function pointer.

	# Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
	while nextSample < totalSamples and not autoStopOuter:
		wasCalledBack = False
		status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(chandle, cFuncPtr, None)
		if not wasCalledBack:
			time.sleep(0.01)

	print('Data has been retrieved from scope')



##################################################################
# Step 7. Process data returned to your application's function. This example is using autoStop, so after the driver has received all the data points requested by the application, it stops the streaming. 
##################################################################
	
	saving_start_time = time.time()

	#Ranges: "PS4000_10MV", "PS4000_20MV", "PS4000_50MV", "PS4000_100MV", "PS4000_200MV", "PS4000_500MV", "PS4000_1V",  "PS4000_2V"
	if chRange == 0: adc_mv_range = 10
	elif chRange == 1: adc_mv_range = 20	
	elif chRange == 2: adc_mv_range = 50
	elif chRange == 3: adc_mv_range = 100
	elif chRange == 4: adc_mv_range = 200			
	elif chRange == 5: adc_mv_range = 500	
	elif chRange == 6: adc_mv_range = 1000	
	elif chRange == 7: adc_mv_range = 2000	

	pico_adc_res = 32767 #+-, value used in "ps4824BlockExample"

	# Convert ADC counts data to mV
	if (0 in meas_channels):
		ChA_mv = bufferCompleteA[:]*(adc_mv_range/pico_adc_res)
	if (1 in meas_channels):
		ChB_mv = bufferCompleteB[:]*(adc_mv_range/pico_adc_res)
	if (2 in meas_channels):
		ChC_mv = bufferCompleteC[:]*(adc_mv_range/pico_adc_res)
	if (3 in meas_channels):
		ChD_mv = bufferCompleteD[:]*(adc_mv_range/pico_adc_res)
	if (4 in meas_channels):
		ChE_mv = bufferCompleteE[:]*(adc_mv_range/pico_adc_res)
	if (5 in meas_channels):
		ChF_mv = bufferCompleteF[:]*(adc_mv_range/pico_adc_res)
	if (6 in meas_channels):
		ChG_mv = bufferCompleteG[:]*(adc_mv_range/pico_adc_res)
	if (7 in meas_channels):
		ChH_mv = bufferCompleteH[:]*(adc_mv_range/pico_adc_res)


	# # Create time data
	time_micros = np.linspace(0, (totalSamples) * actualSampleInterval, totalSamples)


	np.save(dir_name + '\\time_micros.npy', time_micros)
	if (0 in meas_channels):
		np.save(dir_name + '\\ChA_mv.npy', ChA_mv)
	if (1 in meas_channels):
		np.save(dir_name + '\\ChB_mv.npy', ChB_mv)
	if (2 in meas_channels):
		np.save(dir_name + '\\ChC_mv.npy', ChC_mv)
	if (3 in meas_channels):
		np.save(dir_name + '\\ChD_mv.npy', ChD_mv)
	if (4 in meas_channels):
		np.save(dir_name + '\\ChE_mv.npy', ChE_mv)
	if (5 in meas_channels):
		np.save(dir_name + '\\ChF_mv.npy', ChF_mv)
	if (6 in meas_channels):
		np.save(dir_name + '\\ChG_mv.npy', ChG_mv)
	if (7 in meas_channels):
		np.save(dir_name + '\\ChH_mv.npy', ChH_mv)


	# handle = chandle
	status["stop"] = ps.ps4000aStop(chandle)
	assert_pico_ok(status["stop"])

	# Disconnect the scope
	status["close"] = ps.ps4000aCloseUnit(chandle)
	assert_pico_ok(status["close"])
	print(status)

	print('Saving data time: ', np.round((time.time() - saving_start_time)/60, 1))	


	return





def pico_streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
	global nextSample, autoStopOuter, wasCalledBack

	wasCalledBack = True
	destEnd = nextSample + noOfSamples
	sourceEnd = startIndex + noOfSamples

	if (0 in meas_channels):
		bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
	if (1 in meas_channels):
		bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
	if (2 in meas_channels):
		bufferCompleteC[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
	if (3 in meas_channels):
		bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
	if (4 in meas_channels):
		bufferCompleteE[nextSample:destEnd] = bufferEMax[startIndex:sourceEnd]
	if (5 in meas_channels):
		bufferCompleteF[nextSample:destEnd] = bufferFMax[startIndex:sourceEnd]
	if (6 in meas_channels):
		bufferCompleteG[nextSample:destEnd] = bufferGMax[startIndex:sourceEnd]
	if (7 in meas_channels):
		bufferCompleteH[nextSample:destEnd] = bufferHMax[startIndex:sourceEnd]


	nextSample += noOfSamples
	if autoStop:
		autoStopOuter = True

	return




def plot_pico(dir_name, start_time_frac, end_time_frac):
	#Since the files are so big, cannot plot the entire acoustic data for an extended measurement.
	#This function will load and plot the results between the start frac (e.g. 0.1) and end frac (e.g. 0.8)
	#If the requested number of points is too large, function will return without plotting

	plt.figure()

	color_code = 0

	time_vec = (1e-6)*np.load(dir_name + '\\time_micros.npy') #units of nanoseconds
	
	try:
		if (0 in meas_channels):
			ChA_mv = np.load(dir_name + '\\ChA_mv.npy')
			print('Ch. A loaded')
		if (1 in meas_channels):
			ChB_mv = np.load(dir_name + '\\ChB_mv.npy')
			print('Ch. B loaded')
		if (2 in meas_channels):
			ChC_mv = np.load(dir_name + '\\ChC_mv.npy')
			print('Ch. C loaded')
		if (3 in meas_channels):
			ChD_mv = np.load(dir_name + '\\ChD_mv.npy')
			print('Ch. D loaded')
		if (4 in meas_channels):
			ChE_mv = np.load(dir_name + '\\ChE_mv.npy')
			print('Ch. E loaded')
		if (5 in meas_channels):
			ChF_mv = np.load(dir_name + '\\ChF_mv.npy')
			print('Ch. F loaded')
		if (6 in meas_channels):
			ChG_mv = np.load(dir_name + '\\ChG_mv.npy')
			print('Ch. G loaded')
		if (7 in meas_channels):
			ChH_mv = np.load(dir_name + '\\ChH_mv.npy')
			print('Ch. H loaded')

	except:
		print('Tried to load a channel data that did not exist')
		print('Please modify meas_channels array')




	print('Data has been loaded, size = ', np.size(time_vec))


	if (start_time_frac == 0) and (end_time_frac == 0):
		start_ind = 0
		end_ind = np.size(time_vec)

	else:
		start_ind = int(start_time_frac*np.size(time_vec))
		end_ind = int(end_time_frac*np.size(time_vec))


	if (end_ind - start_ind) > 10e6:
		print('Attempting to plot too many points! (', end_ind - start_ind, '), returning to main')
	else:

		colors = plt.cm.jet(np.linspace(0.1, 0.9, 8))

		# Plot data from channel A and B
		if (0 in meas_channels):
			plt.plot(time_vec[start_ind:end_ind], ChA_mv[start_ind:end_ind], color=colors[0], label = 'Ch A')
		if (1 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChB_mv[start_ind:end_ind], color=colors[1],  label = 'Ch B')
		if (2 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChC_mv[start_ind:end_ind], color=colors[2], label = 'Ch C')
		if (3 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChD_mv[start_ind:end_ind], color=colors[3],  label = 'Ch D')
		if (4 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChE_mv[start_ind:end_ind], color=colors[4], label = 'Ch E')
		if (5 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChF_mv[start_ind:end_ind], color=colors[5], label = 'Ch F')
		if (6 in meas_channels):		
			plt.plot(time_vec[start_ind:end_ind], ChG_mv[start_ind:end_ind], color=colors[6], label = 'Ch G')
		if (7 in meas_channels):			
			plt.plot(time_vec[start_ind:end_ind], ChH_mv[start_ind:end_ind], color=colors[7],  label = 'Ch H')

		plt.legend(loc='upper center')
		plt.xlabel('Time (s)')
		plt.ylabel('Voltage (mV)')
		plt.savefig(dir_name + '\\pico_plot.pdf')


	return




if __name__ == "__main__": main()

