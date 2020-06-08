


import numpy as np
import matplotlib.pyplot as plt

import time

from helper_functions import * 
from measurement_routines import * 



def main():

	rm = visa.ResourceManager()
	

# #monitor cooldown
# 	monitor_cooldown()


# #Run IV curve
# 	time_array, I_shunt, Vsample_1, Vsample_2 = run_IV_curve(I_start=0, I_end=100, I_inc=5, test_code = 'test_tape')



# Ramp PSU for CORC quench tests
	# quick_psu_ramp(I_amps= 10, up_ramp_time = 0.5, dwell_time = 1, down_ramp_time = 0.5, setup_time = 10)



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
