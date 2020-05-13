


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

maxSamples = int(2e6) #per segment?
nSegments = 30

#global timebase
samp_freq = 1e6 #1 MHz
samp_dt = 1/(samp_freq)
timebase = int((1e9)*samp_dt/12.5-1) #Manual states "timebase(n) -> sample interval dt = 12.5(ns)*(n+1) -> n = dt/(12.5)-1 with dt in nanoseconds"
print('Calculated time base: ', timebase, ' at sample frequency ', samp_freq)
#timebase = 79 #Manual states "timebase(n) -> sample interval dt = 12.5(ns)*(n+1) -> n = dt/(12.5)-1 with dt in nanoseconds"
timeIntervalns = ctypes.c_float()


# Create buffers ready for assigning pointers for data collection
bufferAMaxArr = []
bufferBMaxArr = []
bufferCMaxArr = []
bufferDMaxArr = []
bufferEMaxArr = []
bufferFMaxArr = []
bufferGMaxArr = []
bufferHMaxArr = []

for i in np.arange(nSegments):
	bufferAMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferBMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferCMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferDMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferEMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferFMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferGMaxArr.append((ctypes.c_int32 * maxSamples)())
	bufferHMaxArr.append((ctypes.c_int32 * maxSamples)())




#To-do: figure out the delay between measurements / trigger offset
# is it 

def main():

	test_name = 'reed_march3_A01'


	dir_name = create_folder(test_name)
	picoscope_measure(dir_name)
	close_pico()

	# plot_pico(dir_name)
	# plot_pico('Results\\reed_march3_A01_save3')


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




def picoscope_measure(dir_name):

##################################################################
#Step 1: open unit with PS4000AOPENUNIT()
##################################################################

	# Open 4000 series PicoScope. Returns handle to chandle for use in future API functions
	status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)

	try: assert_pico_ok(status["openunit"])
	except:
	    powerStatus = status["openunit"]
	    if powerStatus == 286: status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
	    else:raise
	    assert_pico_ok(status["changePowerSource"])


##################################################################
#Step 2: select channels using PS4000ASETCHANNEL()
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
#Step 3: " Set the number of memory segments equal to or greater than the number of captures required using ps4000aMemorySegments(). Use ps4000aSetNoOfCaptures() BEFORE EACH RUN to specify the number of waveforms to capture"
##################################################################

	nMaxSamples=ctypes.c_int32()# returns the number of samples that are available in each segment.
	status["memorySegments"] = ps.ps4000aMemorySegments(chandle, nSegments, ctypes.byref(nMaxSamples))
	assert_pico_ok(status["memorySegments"])

	status["noOfCaptures"] = ps.ps4000aSetNoOfCaptures(chandle, nSegments )
	assert_pico_ok(status["noOfCaptures"])


##################################################################
#Step 4: Set timebase using PS4000AGETTIMEBASE() - "This will indicate the number of samples per channel available for each segment"
##################################################################

	# Get timebase information - 	# handle = chandle, # timebase = 8 = timebase, # noSamples = maxSamples,# pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns),# pointer to maxSamples = ctypes.byref(returnedMaxSamples),# segment index = 0,
	returnedMaxSamples = ctypes.c_int32()
	status["getTimebase2"] = ps.ps4000aGetTimebase2(chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
	assert_pico_ok(status["getTimebase2"])


##################################################################
#Step 5: Set up trigger, can use PS4000ASETSIMPLETRIGGER 
##################################################################
	print('To-do: is this causing a delay between blocks? or does trigger only happen on first block?')
	#Trigger arguments: handle, enable, source, threshold, direction, delay, autoTrigger_ms
	status["trigger"] = ps.ps4000aSetSimpleTrigger(chandle, 1, 0, 1024, 2, 0, 1) #was 100 ms autotrigger_ms
	assert_pico_ok(status["trigger"])

##################################################################
#Step 8(!): Use PS4000ASETDATABUFFER() to tell the driver where your memory buffers are
#Call the function once for each channel/segment combination for which you require data.
#For greater efficiency when doing multiple captures, you can call this function outside the loop, after step 5.
##################################################################


	for i in np.arange(nSegments):
		# (no s) arguments: handle, channel, buffer, bufferlength, segment index, mode
		status["setDataBufferA"] = ps.ps4000aSetDataBuffer(chandle, 0, ctypes.byref(bufferAMaxArr[i]),maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferA"])

		status["setDataBufferB"] = ps.ps4000aSetDataBuffer(chandle, 1, ctypes.byref(bufferBMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferB"])

		status["setDataBufferC"] = ps.ps4000aSetDataBuffer(chandle, 2, ctypes.byref(bufferCMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferC"])

		status["setDataBufferD"] = ps.ps4000aSetDataBuffer(chandle, 3, ctypes.byref(bufferDMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferD"])

		status["setDataBufferE"] = ps.ps4000aSetDataBuffer(chandle, 4, ctypes.byref(bufferEMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferE"])

		status["setDataBufferF"] = ps.ps4000aSetDataBuffer(chandle, 5, ctypes.byref(bufferFMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferF"])

		status["setDataBufferG"] = ps.ps4000aSetDataBuffer(chandle, 6, ctypes.byref(bufferGMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferG"])

		status["setDataBufferH"] = ps.ps4000aSetDataBuffer(chandle, 7, ctypes.byref(bufferHMaxArr[i]), maxSamples, i , 0)
		assert_pico_ok(status["setDataBufferH"])


##################################################################
#Step 6: Start scope using "PS4000ARUNBLOCK"
# Once all the waveforms have been captured, but ready is not complete, call ps4000aGetNoOfProcessedCaptures() to obtain the number of captures processed on the PC.
##################################################################

	status["runBlock"] = ps.ps4000aRunBlock(chandle, 0, maxSamples, timebase, None, 0, None, None)
	assert_pico_ok(status["runBlock"])

##################################################################
#Step 7: Wait until scope is ready using PSA4000ABLOCKREADY()
# Note - using ISREADY here
##################################################################

	# Check for data collection to finish using ps4000aIsReady
	ready = ctypes.c_int32(0)
	check = ctypes.c_int32(0)
	while ready.value == check.value:
	    status["isReady"] = ps.ps4000aIsReady(chandle, ctypes.byref(ready))


##################################################################
#Step 9: Transfer blocks of data using PS4000AGETVALUESBULK()
# Note - step 8 is moved earlier
##################################################################

	overflow = (ctypes.c_int32 * nSegments)()# create overflow loaction
	cmaxSamples = ctypes.c_int32(maxSamples) # create converted type maxSamples
	toSegmentIndex = nSegments-1 
	status["getValuesBulk"] = ps.ps4000aGetValuesBulk(chandle, ctypes.byref(cmaxSamples), 0, toSegmentIndex, 0, 0, ctypes.byref(overflow))
	assert_pico_ok(status["getValuesBulk"])


##################################################################
#Step 10: Retrieve time offset for each data segment using PS4000AGETVLUESTRIGGERTIMEOFFSETBULK64()
# I am not doing this
##################################################################
	print('To-Do: this section doesnt seem to work correctly')
	Times_upper = (ctypes.c_int32*nSegments)()
	Times_lower = (ctypes.c_int32*nSegments)()
	TimeUnits = ctypes.c_char()
	status["GetValuesTriggerTimeOffsetBulk"] = ps.ps4000aGetValuesTriggerTimeOffsetBulk(chandle, ctypes.byref(Times_upper), ctypes.byref(Times_lower), ctypes.byref(TimeUnits), 0, toSegmentIndex)
	assert_pico_ok(status["GetValuesTriggerTimeOffsetBulk"])

##################################################################
#Step 11: display data
##################################################################

	# find maximum ADC count value
	maxADC = ctypes.c_int16()	
	status["maximumValue"] = ps.ps4000aMaximumValue(chandle, ctypes.byref(maxADC))

	#Save data in each block of memory
	for i in np.arange(nSegments):
		# convert ADC counts data to mV
		adc2mVChAMax =  adc2mV(bufferAMaxArr[i], chRange, maxADC)
		adc2mVChBMax =  adc2mV(bufferBMaxArr[i], chRange, maxADC)
		adc2mVChCMax =  adc2mV(bufferCMaxArr[i], chRange, maxADC)
		adc2mVChDMax =  adc2mV(bufferDMaxArr[i], chRange, maxADC)
		adc2mVChEMax =  adc2mV(bufferEMaxArr[i], chRange, maxADC)
		adc2mVChFMax =  adc2mV(bufferFMaxArr[i], chRange, maxADC)
		adc2mVChGMax =  adc2mV(bufferGMaxArr[i], chRange, maxADC)
		adc2mVChHMax =  adc2mV(bufferHMaxArr[i], chRange, maxADC)
		time_ns = np.linspace(0, (cmaxSamples.value) * timeIntervalns.value, cmaxSamples.value)

		np.save(dir_name + '\\time_ns' + str(i) + '.npy', time_ns)
		np.save(dir_name + '\\ChA_' + str(i) + '.npy', adc2mVChAMax[:])
		np.save(dir_name + '\\ChB_' + str(i) + '.npy', adc2mVChBMax[:])
		np.save(dir_name + '\\ChC_' + str(i) + '.npy', adc2mVChCMax[:])
		np.save(dir_name + '\\ChD_' + str(i) + '.npy', adc2mVChDMax[:])
		np.save(dir_name + '\\ChE_' + str(i) + '.npy', adc2mVChEMax[:])
		np.save(dir_name + '\\ChF_' + str(i) + '.npy', adc2mVChFMax[:])
		np.save(dir_name + '\\ChG_' + str(i) + '.npy', adc2mVChGMax[:])
		np.save(dir_name + '\\ChH_' + str(i) + '.npy', adc2mVChHMax[:])






def close_pico():

	status["stop"] = ps.ps4000aStop(chandle)
	assert_pico_ok(status["stop"])
	status["close"] = ps.ps4000aCloseUnit(chandle)
	assert_pico_ok(status["close"])
	print(status)

	return






def plot_pico(dir_name):


	plt.figure()

	color_code = 0
	for i in np.arange(nSegments):

		time_vec = (1e-9)*np.load(dir_name + '\\time_ns' + str(i) + '.npy') #units of nanoseconds
		ChA = np.load(dir_name + '\\ChA_' + str(i) + '.npy')
		ChB = np.load(dir_name + '\\ChB_' + str(i) + '.npy')
		ChC = np.load(dir_name + '\\ChC_' + str(i) + '.npy')
		ChD = np.load(dir_name + '\\ChD_' + str(i) + '.npy')
		ChE = np.load(dir_name + '\\ChE_' + str(i) + '.npy')
		ChF = np.load(dir_name + '\\ChF_' + str(i) + '.npy')
		ChG = np.load(dir_name + '\\ChG_' + str(i) + '.npy')
		ChH = np.load(dir_name + '\\ChH_' + str(i) + '.npy')

		colors = plt.cm.jet(np.linspace(0.1, 0.9, 8*nSegments))
		# Plot data from channel A and B
		plt.plot(time_vec, ChA, color=colors[i], label = 'Ch A-' + str(i))
		plt.plot(time_vec, ChB, color=colors[nSegments + i],  label = 'Ch B-' + str(i))
		plt.plot(time_vec, ChC, color=colors[2*nSegments + i], label = 'Ch C-' + str(i))
		plt.plot(time_vec, ChD, color=colors[3*nSegments + i],  label = 'Ch D-' + str(i))
		plt.plot(time_vec, ChE, color=colors[4*nSegments + i], label = 'Ch E-' + str(i))
		plt.plot(time_vec, ChF, color=colors[5*nSegments + i], label = 'Ch F-' + str(i))
		plt.plot(time_vec, ChG, color=colors[6*nSegments + i], label = 'Ch G-' + str(i))
		plt.plot(time_vec, ChH, color=colors[7*nSegments + i],  label = 'Ch H-' + str(i))

	plt.legend(loc='upper center')
	plt.xlabel('Time (s)')
	plt.ylabel('Voltage (mV)')
	plt.show()


	return




if __name__ == "__main__": main()

