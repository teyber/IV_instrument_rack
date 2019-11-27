


# import serial
import sys
import time
import visa
import numpy as np
import matplotlib.pyplot as plt




##########################################################################################
#Start Nanovoltmeter

#This function initiates the Agilent 34420A nanovolt meter
#and gets is ready to start returning single readings.
#Note - there are two channels. Must select channel before querying read
def init_nanovm():

	nanovm = rm.open_resource("TCPIP::192.168.100.10::gpib0,22::INSTR")
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
	nanovm.write("SENSE1:VOLT:DC:range 0.01")
	nanovm.write("SENSE2:VOLT:DC:range 0.01")
	nanovm.write("SENSE1:VOLT:DC:NPLC 1.0")
	nanovm.write("SENSE2:VOLT:DC:NPLC 1.0")
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
	v_nvm1 = float(nanovm.read())

	return v_nvm



#End Nanovoltmeter
##########################################################################################




##########################################################################################
#Start Keithley 2010


#This function initiates the Keithley 2010 multimeter
#and gets is ready to start returning single readings
#upon receiving a :READ? command
def init_dvm():

	max_shunt_voltage = 10

	dvm = rm.open_resource("TCPIP::192.168.100.10::gpib0,8::INSTR")
	dvm.write('*IDN?')
	print(dvm.read())

	dvm.timeout = 100
	dvm.write_termination = '\n'
	dvm.read_termination = '\n'
	dvm.write("*RST")
	time.sleep(0.1)
	dvm.write(":SENS:FUNC \'VOLTAGE:DC\'")
	time.sleep(0.1)
	dvm.write(":SENS:VOLT:DC:range "+str(max_shunt_voltage))
	dvm.write(":SENS:VOLT:DC:NPLC 1.0")
	dvm.write(":TRIG:COUNT 1")
	dvm.write(":SAMPLE:COUNT 1")
	dvm.write(":TRIG:SOUR IMM")
	time.sleep(0.1)

	return dvm



#Return voltage reading from keithley voltmeter
def get_dvm(dvm):

	dvm.write(':READ?')
	v_dvm = float(dvm.read())

	return v_dvm


#End Keithley 2010
##########################################################################################







##########################################################################################
#Start Sorenson PSU

#This function initiates the Sorenson SGA 10/1200 power supply 
#A maximum voltage is programmed
def init_sorenson_psu(max_voltage):

	sorenson_psu = rm.open_resource("TCPIP::192.168.100.10::gpib0,3::INSTR") #"TCPIP::192.168.100.1::1394::SOCKET"
	sorenson_psu.timeout = 100
	sorenson_psu.write_termination = '\n'
	sorenson_psu.read_termination = '\n'
	sorenson_psu.write("*IDN?")
	print(sorenson_psu.read())

	# sorenson_psu.write("*CLS")
	time.sleep(0.2)
	sorenson_psu.write("*RST")
	time.sleep(0.5)
	sorenson_psu.write('SOUR:VOLT ' + str(max_voltage))
	time.sleep(0.1)
	sorenson_psu.write('SOUR:CURR 0')
	time.sleep(0.1)

	return sorenson_psu



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


#END Sorenson PSU
##########################################################################################





# ##########################################################################################
# #Start Agilent PSU


# #This function initiates the Agilent E3631A power supply
# #Note - this is the SMALL power supply, not for superconducting samples!
# def init_agilent_psu():

# 	agilent_psu = rm.open_resource("TCPIP::192.168.100.10::gpib0,7::INSTR")
# 	agilent_psu.write('*IDN?')
# 	print(agilent_psu.read())
# 	agilent_psu.timeout = 100
# 	agilent_psu.write_termination = '\n'
# 	agilent_psu.read_termination = '\n'


# 	agilent_psu.write("*RST")
# 	time.sleep(0.1)

# 	agilent_psu.write("INST:SEL P6V")
# 	agilent_psu.write("VOLT:TRIG 5") #5 volts
# 	agilent_psu.write("CURR:TRIG 0.1") #0.1 amps

# 	time.sleep(0.5)

# 	agilent_psu.write("TRIG:SOUR BUS")

# 	time.sleep(0.5)

# 	agilent_psu.write("INIT")

# 	return agilent_psu

# #End Agilent PSU
# ##########################################################################################










