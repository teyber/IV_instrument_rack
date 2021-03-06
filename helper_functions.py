

import visa
import numpy as np
import time
import os





##########################################################################################
#Create results folder

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



#End results folder
##########################################################################################






##########################################################################################
#Start Nanovoltmeter

#This function initiates the Agilent 34420A nanovolt meter
#and gets is ready to start returning single readings.
#Note - there are two channels. Must select channel before querying read
def init_nanovm(rm, max_voltage, NPLC):

	nanovm = rm.open_resource("TCPIP::169.254.58.10::gpib0,22::INSTR")
	#nanovm = rm.open_resource("TCPIP::192.168.100.10::gpib0,22::INSTR")	
	nanovm.write('*IDN?')
	print(nanovm.read())

	nanovm.write('*RST')
	time.sleep(0.1)

	nanovm.write_termination = '\n'
	nanovm.read_termination = '\n'
	nanovm.timeout = 500

	nanovm.write("SENSE1:FUNC \'VOLTAGE:DC\'")
	nanovm.write("SENSE2:FUNC \'VOLTAGE:DC\'")
	time.sleep(0.1)
	nanovm.write("SENSE1:VOLT:DC:range " + str(np.round(max_voltage, 4)))
	nanovm.write("SENSE2:VOLT:DC:range " + str(np.round(max_voltage, 4)))
	nanovm.write("SENSE1:VOLT:DC:NPLC " + str(np.round(NPLC, 3)))
	nanovm.write("SENSE2:VOLT:DC:NPLC " + str(np.round(NPLC,3)))
	time.sleep(0.1)

	return nanovm



#Return voltage reading from specified channel of nanovolt meter
def get_nanovm(nanovm, ch_num):

	if ch_num == 1:	
		nanovm.write('ROUT:TERM FRON1')
	elif ch_num == 2: 
		nanovm.write('ROUT:TERM FRON2')
	else:
		print('Incorrect channel number. Defaulting to channel 1')
		nanovm.write('ROUT:TERM FRON1')

	nanovm.write('READ?')
	v_nvm = float(nanovm.read())

	return v_nvm



#End Nanovoltmeter
##########################################################################################




##########################################################################################
#Start Keithley 2010

#This function initiates the Keithley 2010 multimeter
#and gets is ready to start returning single readings
#upon receiving a :READ? command
def init_dvm(rm, max_voltage, NPLC):

	dvm = rm.open_resource("TCPIP::169.254.58.10::gpib0,8::INSTR")
	#dvm = rm.open_resource("TCPIP::192.168.100.10::gpib0,8::INSTR")

	
	dvm.write('*IDN?')
	print(dvm.read())

	dvm.timeout = 100
	dvm.write_termination = '\n'
	dvm.read_termination = '\n'
	dvm.write("*RST")
	time.sleep(0.1)
	dvm.write(":SENS:FUNC \'VOLTAGE:DC\'")
	time.sleep(0.1)
	dvm.write(":SENS:VOLT:DC:range "+ str(np.round(max_voltage, 4))) 
	dvm.write(":SENS:VOLT:DC:NPLC " + str(np.round(NPLC, 1)))
	dvm.write(":TRIG:COUNT 1")
	dvm.write(":SAMPLE:COUNT 1")
	dvm.write(":TRIG:SOUR IMM")
	time.sleep(0.1)

	return dvm



#Get voltage reading from keithley voltmeter
#Return both the raw voltage and calculated shunt resistance
def get_dvm(dvm):

	Rshunt = (50/1000)/1000 #1200A Sorenson PSU has 50 mV/1kA written on shunt resistor
	dvm.write(':READ?')
	v_dvm = float(dvm.read())
	Isample = v_dvm/Rshunt

	return v_dvm, Isample



#End Keithley 2010
##########################################################################################





##########################################################################################
#Start Agilent 33210A function generator

#This function initiates the Agilent 33210A function generator
def init_waveform(rm):

	#waveform = rm.open_resource("TCPIP::192.168.100.10::gpib0,15::INSTR")
	waveform = rm.open_resource("TCPIP::169.254.58.10::gpib0,15::INSTR")

	
	dvm.write('*IDN?')
	print(dvm.read())

	waveform.timeout = 100
	waveform.write_termination = '\n'
	waveform.read_termination = '\n'
	waveform.write("*RST")
	time.sleep(0.1)


	return waveform




#End Agilent 33210A
##########################################################################################




##########################################################################################
#Start Sorenson PSU

#This function initiates the Sorenson SGA 10/1200 power supply 
#A maximum voltage is programmed
def init_sorenson_psu(rm, max_voltage):

	#sorenson = rm.open_resource("TCPIP::192.168.100.10::gpib0,7::INSTR") #"TCPIP::192.168.100.1::1394::SOCKET"
	sorenson = rm.open_resource("TCPIP::169.254.58.10::gpib0,7::INSTR") #"TCPIP::192.168.100.1::1394::SOCKET"

	
	sorenson.timeout = 100
	sorenson.write_termination = '\n'
	sorenson.read_termination = '\n'
	sorenson.write("*IDN?")
	print(sorenson.read())

	# sorenson_psu.write("*CLS")
	time.sleep(0.2)
	sorenson.write("*RST")
	time.sleep(0.5)
	sorenson.write('SOUR:VOLT ' + str(max_voltage))
	time.sleep(0.1)
	sorenson.write('SOUR:CURR 0')
	time.sleep(0.1)

	return sorenson



#Program the Sorenson PSU to a new current value
def set_sorenson_psu(sorenson_psu, I_mag):

	sorenson_psu.write("SOUR:CURR " + str(np.round(I_mag,2)))

	return



#Program the sorenson PSU from its existing current to a specified value
# over a specified time
def ramp_sorenson_psu(sorenson_psu, I_ramp_time, I_ramp_mag):

	sorenson_psu.write('SOUR:CURR:RAMP:TRIG ' + str(I_ramp_mag) + ' ' + str(I_ramp_time))
	time.sleep(0.1)
	sorenson_psu.write('TRIG:RAMP')

	return


#Used to disable and re-enable 
def modify_sorenson_limits(sorenson_psu, max_I, max_V):

	sorenson_psu.write('SOUR:CURR '+ str(max_I))
	time.sleep(0.1)
	sorenson_psu.write('SOUR:VOLT ' + str(max_V))
	time.sleep(0.1)

	return


#END Sorenson PSU
##########################################################################################








