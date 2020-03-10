


import numpy as np
import matplotlib.pyplot as plt

import time

from helper_functions import * 
from measurement_routines import * 



def main():

	rm = visa.ResourceManager()

	cryo = rm.open_resource("TCPIP::169.254.58.10::gpib0,12::INSTR") #"TCPIP::192.168.100.1::1394::SOCKET"
	cryo.write('*IDN?')
	print(cryo.read())

	

# #monitor cooldown
# 	monitor_cooldown()


# #Run IV curve
# 	time_array, I_shunt, Vsample_1, Vsample_2 = run_IV_curve(I_start=0, I_end=100, I_inc=5, test_code = 'test_tape')

	#quick_psu_ramp()


	#quick_psu_ramp()

	return




def quick_psu_ramp():

	rm = visa.ResourceManager()
	sorenson = init_sorenson_psu(rm, max_voltage=5)


	I_amps = 1000

	ramp_time = 1.0
	dwell_time = 0.01#

	time.sleep(5) #give me time to run to yokogawa
	print("\a")
	time.sleep(4)
	print("\a")
	time.sleep(1)

	ramp_sorenson_psu(sorenson, ramp_time, I_amps) #linear ramp up
	time.sleep(ramp_time + dwell_time) #0.8*ramp_time

	ramp_sorenson_psu(sorenson, 0.1, 0) #Ramp to 0 amps over 0.1 seconds
	#set_sorenson_psu(sorenson, 0)#immediately go to 0 amps


	return




def run_PSU_ramp():
	# power supply commands
	rm = visa.ResourceManager()
	sorenson = init_sorenson_psu(rm, max_voltage=5)


	I_amps = 750#1000

	ramp_time = 0.1 #seconds #10
	dwell_time = 1# 0.2 #0.2 seconds for fast ramp


	time.sleep(10) 

	ramp_sorenson_psu(sorenson, ramp_time, I_amps)
	time.sleep(ramp_time + dwell_time)
	ramp_sorenson_psu(sorenson, ramp_time, 0)



	#ramp_sorenson_psu(sorenson, 1, 0)	


	#print('Current: ', I_amps)




if __name__ == "__main__": main()












	# I_shunt = []
	# V_dcct = []
	# I_vec = np.array([0, 100, 200, 300, 400, 500])

	# for i in np.arange(np.size(I_vec)):

	# 	ramp_sorenson_psu(sorenson, 0.25, I_vec[i])
	# 	time.sleep(0.75)
	# 	I_shunt.append(-get_dvm(dvm)[1])
	# 	V_dcct.append(get_nanovm(nanovm, ch_num=1))

	
	# ramp_sorenson_psu(sorenson, 0.25, 0)
	# time.sleep(1)
	# I_shunt.append(-get_dvm(dvm)[1])
	# V_dcct.append(get_nanovm(nanovm, ch_num=1))


	# print('Ishunt.txt', np.asarray(I_shunt))
	# print('V_ddct.txt', np.asarray(V_dcct))


	# np.savetxt('Iset.txt', I_vec)
	# np.savetxt('Ishunt.txt', np.asarray(I_shunt))
	# np.savetxt('V_ddct.txt', np.asarray(V_dcct))


	# plt.figure()
	# plt.plot(I_shunt, V_dcct, 'ko--')
	# plt.savefig('v_dcct.pdf')
