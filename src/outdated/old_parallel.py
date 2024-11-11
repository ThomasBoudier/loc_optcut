from tools import *
from z3 import *
from multiprocessing import Pool
from random import randint

from tools import auto_verification
from time import time

CHUNKSIZE = 2**14

PROCESSES = 2**8   
### this code is "useless" as in "it's outdated and better functions do it". However it display a simple example of how the parallelization is to be done.
def executor(file_number):

    file_id = '{0:08b}'.format(file_number)
    with open('2-2-3_gadgets/data/slices/slice_'+file_id, 'r') as f:
        starting_value = int(file_id+f.readline(), 2)

    for k in range(CHUNKSIZE):
        input = starting_value + k
        input_b = '{0:030b}'.format(input) #=total input even counting the slide id
        #print(input_b, input, type(input_b), type(input))
        if auto_verification(input_b):
            if hard_solver(input_b)==False:
                with open('2-2-3_gadgets/data/save_to_look_at.txt', 'a') as f:
                    f.write(input_b+'\n')
    with open('2-2-3_gadgets/data/slices/slice_'+file_id, 'w') as f:
        f.write(input_b[8:])

def parallel_executor():
    i = 0
    step = 100*(2**14/2**22) #=chuksize/total work per slice
    progress = 0    
    t0 = time()
    print('commencing process...')
    while(progress<100):
        p = Pool(4)
        p.map(executor, range(PROCESSES))
        i+=1
        progress += step
        os.system('clear')
        #TODO to have a coherent print status think to change workload when changing the problem
        print('%d iteration done - %d done sine last execution - time since computation beggining: %d' %(i, progress, time()-t0))
#cleanup()
#parallel_executor()



