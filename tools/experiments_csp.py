import time
import subprocess

N = 1024

with open('./csp_res.csv', 'w') as file:
    file.write('')

for i in range(1, N+1):
    start_time = time.perf_counter()
    result = subprocess.run(['python3', 'varanus-python/varanus.py', 'build-only', f'csp{i}.yaml'], capture_output=True, text=True)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    with open('./csp_res.csv', 'a') as file:
        file.write(f'{i}; {elapsed_time}\n')
       
