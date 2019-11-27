


# import serial
import sys
import time
import visa

import numpy as np
import matplotlib.pyplot as plt




rm = visa.ResourceManager()



max_voltage = 1.0 #Max voltage of 0.2 volts

I_ramp_time = 0.1 #seconds
I_ramp_mag = 1000 #amps
peak_dwell_time = 0.2 #seconds




def main():



	init_agilent_psu()


#Initialize instruments
	nanovm = init_nanovm()
	dvm = init_dvm()



#Ask meters for readings
	nanovm.write('ROUT:TERM FRON1')
	nanovm.write('READ?')
	v_nvm1 = float(nanovm.read())

	nanovm.write('ROUT:TERM FRON2')
	nanovm.write('READ?')
	v_nvm2 = float(nanovm.read())

	dvm.write(':READ?')
	v_dvm = float(dvm.read())

	print(v_nvm1)
	print(v_nvm2)
	print(v_dvm)


	return



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


	# psu = rm.open_resource("TCPIP::192.168.100.10::gpib0,21::INSTR")
	# psu.write('*IDN?')
	# print(psu.read())

	#rm.open_resource("TCPIP::192.168.100.10::gpib0,3::INSTR")





#This function initiates the Agilent E3631A power supply
#Note - this is the SMALL power supply, not for superconducting samples!
def init_agilent_psu():

	agilent_psu = rm.open_resource("TCPIP::192.168.100.10::gpib0,7::INSTR")
	agilent_psu.write('*IDN?')
	print(agilent_psu.read())


	agilent_psu.write("*RST")
	time.sleep(0.1)

	agilent_psu.write("INST:SEL P6V")
	agilent_psu.write("VOLT:TRIG 5") #5 volts
	agilent_psu.write("CURR:TRIG 0.1") #0.1 amps

	time.sleep(2)

	agilent_psu.write("TRIG:SOUR BUS")

	time.sleep(2)

	agilent_psu.write("INIT")

	return agilent_psu





def do_not_run():

	psu = rm.open_resource("TCPIP::192.168.100.10::gpib0,3::INSTR") #"TCPIP::192.168.100.1::1394::SOCKET"
	psu.timeout = 100
	psu.write_termination = '\n'
	psu.read_termination = '\n'

	psu.write("*IDN?")
	print(psu.read())

	psu.write("*CLS")
	time.sleep(0.2)
	psu.write("*RST")
	time.sleep(0.5)

	psu.write('SOUR:VOLT ' + str(max_voltage))
	time.sleep(0.2)

	psu.write('SOUR:CURR 0')
	time.sleep(0.2)



	#Tell PSU to ramp
	psu.write('SOUR:CURR:RAMP:TRIG ' + str(I_ramp_mag) + ' ' + str(I_ramp_time))
	time.sleep(0.1)
	psu.write('TRIG:RAMP')

	time.sleep(peak_dwell_time + I_ramp_time)
	psu.write("SOUR:CURR 0")

	time.sleep(0.1)



	return









if __name__ == "__main__": main()