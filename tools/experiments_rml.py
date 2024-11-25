import time
import subprocess

N = 1024

path_to_rml_compiler = '/media/angelo/WorkData/git/ROSMonitoring3/ROSMonitoring/oracle/RMLOracle/rml/rml-compiler.jar'

with open('./rml_res.csv', 'w') as file:
    file.write('')

for i in range(1, N+1):
    start_time = time.perf_counter()
    result = subprocess.run(['java', '-jar', path_to_rml_compiler, '--input', f'./rml/rml{i}.rml', '--output', './tmp.pl'], capture_output=True, text=True)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    with open('./rml_res.csv', 'a') as file:
        file.write(f'{i}; {elapsed_time}\n')
       
