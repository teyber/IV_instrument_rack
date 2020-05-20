


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

#Ranges: "PS4000_10MV", "PS4000_20MV", "PS4000_50MV", "PS4000_100MV", "PS4000_200MV", "PS4000_500MV", "PS4000_1V",  "PS4000_2V",
chRange = 4



sample_period_microseconds = 5 
sizeOfOneBuffer = int(0.2e6)
#capture 1 second at 200 KHz

#Record for 5 minutes
numBuffersToCapture = int(60*20)

totalSamples = sizeOfOneBuffer * numBuffersToCapture




#HAVING ISSUES PASSING IN GLOBALLY SCOPED ARGS INTO CALL BACK
#Current solution is to pull them out here
nextSample = 0


# We need a big buffer, not registered with the driver, to keep our complete capture in.
bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteC = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteD = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteE = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteF = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteG = np.zeros(shape=totalSamples, dtype=np.int16)
bufferCompleteH = np.zeros(shape=totalSamples, dtype=np.int16)



# Create buffers ready for assigning pointers for data collection
bufferAMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferBMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferCMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferDMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferEMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferFMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferGMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)
bufferHMax = np.zeros(shape = sizeOfOneBuffer, dtype=np.int16)



#To-do: figure out the delay between measurements / trigger offset
# is it 

def main():

	tot_start_time = time.time()

	test_name = 'reed_may18_A01'
	dir_name = create_folder(test_name)


	stream_picoscope(dir_name)
	print('Streaming and saving time: ', np.round((time.time() - tot_start_time)/60, 1))	


	# plot_start_time = time.time()
	# plot_pico(dir_name)
	# print('Plotting time: ', np.round((time.time() - plot_start_time)/60, 1))	


	# plot_pico('Results\\reed_may18_A01_save4')

	print('Elapsed time: ', np.round((time.time() - tot_start_time)/60, 2))	
	return




def create_folder(test_code_0):

	#Create a folder for the test, make sure we do not overwrite any prior tests
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
	status["setChA"] = ps.ps4000aSetChannel(chandle, 0, 1, 1, chRange, 0)
	assert_pico_ok(status["setChA"])

	status["setChB"] = ps.ps4000aSetChannel(chandle, 1, 1, 1, chRange, 0)
	assert_pico_ok(status["setChB"])

	status["setChC"] = ps.ps4000aSetChannel(chandle, 2, 1, 1, chRange, 0)
	assert_pico_ok(status["setChC"])

	status["setChD"] = ps.ps4000aSetChannel(chandle, 3, 1, 1, chRange, 0)
	assert_pico_ok(status["setChD"])

	status["setChE"] = ps.ps4000aSetChannel(chandle, 4, 1, 1, chRange, 0)
	assert_pico_ok(status["setChE"])

	status["setChF"] = ps.ps4000aSetChannel(chandle, 5, 1, 1, chRange, 0)
	assert_pico_ok(status["setChF"])

	status["setChG"] = ps.ps4000aSetChannel(chandle, 6, 1, 1, chRange, 0)
	assert_pico_ok(status["setChG"])

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

	status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'], bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersA"])

	status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'], bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersB"])

	status["setDataBuffersC"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_C'], bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersC"])

	status["setDataBuffersD"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_D'], bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersD"])

	status["setDataBuffersE"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_E'], bufferEMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersE"])

	status["setDataBuffersF"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_F'], bufferFMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersF"])

	status["setDataBuffersG"] = ps.ps4000aSetDataBuffers(chandle, ps.PS4000A_CHANNEL['PS4000A_CHANNEL_G'], bufferGMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), None, sizeOfOneBuffer, memory_segment, ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
	assert_pico_ok(status["setDataBuffersG"])

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

	# nextSample = 0
	autoStopOuter = False
	wasCalledBack = False


	# Convert the python function into a C function pointer.
	cFuncPtr = ps.StreamingReadyType(pico_streaming_callback)

	# Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
	while nextSample < totalSamples and not autoStopOuter:
		wasCalledBack = False
		status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(chandle, cFuncPtr, None)
		if not wasCalledBack:
			# If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
			# again.
			time.sleep(0.01)

	print("Done grabbing values.")




##################################################################
# Step 7. Process data returned to your application's function. This example is using autoStop, so after the driver has received all the data points requested by the application, it stops the streaming. 
##################################################################
	
	print('Data has been retrieved from scope')


	# Find maximum ADC count value
	maxADC = ctypes.c_int16(sample_period_microseconds)
	status["maximumValue"] = ps.ps4000aMaximumValue(chandle, ctypes.byref(maxADC))
	assert_pico_ok(status["maximumValue"])

	saving_start_time = time.time()



	# Convert ADC counts data to mV
	# adc2mVChAMax = adc2mV(bufferCompleteA, chRange, maxADC)
	# adc2mVChBMax = adc2mV(bufferCompleteB, chRange, maxADC)
	# adc2mVChCMax = adc2mV(bufferCompleteC, chRange, maxADC)
	# adc2mVChDMax = adc2mV(bufferCompleteD, chRange, maxADC)
	# adc2mVChEMax = adc2mV(bufferCompleteE, chRange, maxADC)
	# adc2mVChFMax = adc2mV(bufferCompleteF, chRange, maxADC)
	# adc2mVChGMax = adc2mV(bufferCompleteG, chRange, maxADC)
	# adc2mVChHMax = adc2mV(bufferCompleteH, chRange, maxADC)


	# print('line 268: ', time.time() - saving_start_time)


	# # Create time data
	time_micros = np.linspace(0, (totalSamples) * actualSampleInterval, totalSamples)


	np.save(dir_name + '\\time_micros.npy', time_micros)
	

	np.save(dir_name + '\\time_micros.npy', time_micros)
	np.save(dir_name + '\\ChA.npy', bufferCompleteA)
	np.save(dir_name + '\\ChB.npy', bufferCompleteB)
	np.save(dir_name + '\\ChC.npy', bufferCompleteC)
	np.save(dir_name + '\\ChD.npy', bufferCompleteD)
	np.save(dir_name + '\\ChE.npy', bufferCompleteE)
	np.save(dir_name + '\\ChF.npy', bufferCompleteF)
	np.save(dir_name + '\\ChG.npy', bufferCompleteG)
	np.save(dir_name + '\\ChH.npy', bufferCompleteH)

	# np.save(dir_name + '\\ChA.npy', adc2mVChAMax[:])
	# np.save(dir_name + '\\ChB.npy', adc2mVChBMax[:])
	# np.save(dir_name + '\\ChC.npy', adc2mVChCMax[:])
	# np.save(dir_name + '\\ChD.npy', adc2mVChDMax[:])
	# np.save(dir_name + '\\ChE.npy', adc2mVChEMax[:])
	# np.save(dir_name + '\\ChF.npy', adc2mVChFMax[:])
	# np.save(dir_name + '\\ChG.npy', adc2mVChGMax[:])
	# np.save(dir_name + '\\ChH.npy', adc2mVChHMax[:])


	# print('line 286: ', time.time() - saving_start_time)


	# handle = chandle
	status["stop"] = ps.ps4000aStop(chandle)
	assert_pico_ok(status["stop"])

	# Disconnect the scope
	# handle = chandle
	status["close"] = ps.ps4000aCloseUnit(chandle)
	assert_pico_ok(status["close"])

	# Display status returns
	print(status)


	print('Saving data time: ', np.round((time.time() - saving_start_time)/60, 1))	


	return





def pico_streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
	global nextSample, autoStopOuter, wasCalledBack

	wasCalledBack = True
	destEnd = nextSample + noOfSamples
	sourceEnd = startIndex + noOfSamples

	bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
	bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
	bufferCompleteC[nextSample:destEnd] = bufferCMax[startIndex:sourceEnd]
	bufferCompleteD[nextSample:destEnd] = bufferDMax[startIndex:sourceEnd]
	bufferCompleteE[nextSample:destEnd] = bufferEMax[startIndex:sourceEnd]
	bufferCompleteF[nextSample:destEnd] = bufferFMax[startIndex:sourceEnd]
	bufferCompleteG[nextSample:destEnd] = bufferGMax[startIndex:sourceEnd]
	bufferCompleteH[nextSample:destEnd] = bufferHMax[startIndex:sourceEnd]



	nextSample += noOfSamples
	if autoStop:
		autoStopOuter = True

	return






def plot_pico(dir_name):


	plt.figure()

	color_code = 0

	time_vec = (1e-6)*np.load(dir_name + '\\time_micros.npy') #units of nanoseconds
	ChA = np.load(dir_name + '\\ChA.npy')
	ChB = np.load(dir_name + '\\ChB.npy')
	ChC = np.load(dir_name + '\\ChC.npy')
	ChD = np.load(dir_name + '\\ChD.npy')
	ChE = np.load(dir_name + '\\ChE.npy')
	ChF = np.load(dir_name + '\\ChF.npy')
	ChG = np.load(dir_name + '\\ChG.npy')
	ChH = np.load(dir_name + '\\ChH.npy')

	colors = plt.cm.jet(np.linspace(0.1, 0.9, 8))
	# Plot data from channel A and B
	plt.plot(time_vec, ChA, color=colors[0], label = 'Ch A')
	plt.plot(time_vec, ChB, color=colors[1],  label = 'Ch B')
	plt.plot(time_vec, ChC, color=colors[2], label = 'Ch C')
	plt.plot(time_vec, ChD, color=colors[3],  label = 'Ch D')
	plt.plot(time_vec, ChE, color=colors[4], label = 'Ch E')
	plt.plot(time_vec, ChF, color=colors[5], label = 'Ch F')
	plt.plot(time_vec, ChG, color=colors[6], label = 'Ch G')
	plt.plot(time_vec, ChH, color=colors[7],  label = 'Ch H')

	plt.legend(loc='upper center')
	plt.xlabel('Time (s)')
	plt.ylabel('Voltage (mV)')
	plt.show()


	return




if __name__ == "__main__": main()

