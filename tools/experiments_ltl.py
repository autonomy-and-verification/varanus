import os
import spot
import time

N = 1024

with open('./ltl_res.csv', 'w') as file:
    file.write('')

for i in range(1, N+1):
    with open(f'./ltl/ltl{i}.txt', 'r') as file:
        ltl = file.read()
        print(ltl)
        start_time = time.perf_counter()
        monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        with open('./ltl_res.csv', 'a') as file:
            file.write(f'{i}; {elapsed_time}\n')
