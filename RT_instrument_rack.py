


import numpy as np
import matplotlib.pyplot as plt
from helper_functions import * 
from measurement_routines import * 



def main():


# #monitor cooldown
# 	monitor_cooldown()


#Run IV curve
	time_array, I_shunt, Vsample_1, Vsample_2 = run_IV_curve(I_start=0, I_end=100, I_inc=5, test_code = 'test_tape')




if __name__ == "__main__": main()