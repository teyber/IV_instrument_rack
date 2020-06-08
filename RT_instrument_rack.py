


import numpy as np
import matplotlib.pyplot as plt

import time

from helper_functions import * 
from measurement_routines import * 



def main():

	rm = visa.ResourceManager()
	

# #monitor cooldown
# 	monitor_cooldown(rm)


# #Run IV curve, measure both up and down ramps
	test_code = 'corc_june_9_2020'

	#Initialize instruments
	nanovm = init_nanovm(rm, max_voltage = 0.01, NPLC = 1)
	dvm = init_dvm(rm, max_voltage = 0.1, NPLC = 0.1)
	sorenson = init_sorenson_psu(rm, max_voltage = 3)

	#Ramp up and down
	I_max = 20
	dA = 5
	run_IV_curve(rm, nanovm, dvm, sorenson, 0, I_max, dA, test_code, disable_psu = False, safe_mode = True) #ramp up, leave PSU energized
	time.sleep(0.1)
	run_IV_curve(rm, nanovm, dvm, sorenson, I_max, 0, -dA, test_code, disable_psu = True, safe_mode = True) #ramp up, leave PSU energized


# Ramp PSU for CORC quench tests
	# quick_psu_ramp(rm, I_amps= 10, up_ramp_time = 0.5, dwell_time = 1, down_ramp_time = 0.5, setup_time = 10)



	return








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
