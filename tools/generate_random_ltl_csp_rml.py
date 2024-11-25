import ltl2csp_rml
import spot
import string
import shutil
import os

N = 1200
S = 100

if os.path.exists('./ltl/'):
    shutil.rmtree('./ltl/')
if os.path.exists('./csp/'):
    shutil.rmtree('./csp/')
if os.path.exists('./rml/'):
    shutil.rmtree('./rml/')

os.makedirs('./ltl/', exist_ok=True)
os.makedirs('./csp/', exist_ok=True)
os.makedirs('./rml/', exist_ok=True)

def length(f):
    global count
    if f._is(spot.op_Equiv)  or f._is(spot.op_Implies)  or f._is(spot.op_And) or f._is(spot.op_Or) or f._is(spot.op_Xor) or f._is(spot.op_X) or f._is(spot.op_U) or f._is(spot.op_R) or f._is(spot.op_W) or f._is(spot.op_G) or f._is(spot.op_F) or f._is(spot.op_M):
        count = count + 1
    return False

size_ltl = 5

ltl_gen = spot.randltl(list(string.ascii_lowercase), tree_size=size_ltl)

i = 1
while(True):
    if i > N: break
    ltl = next(ltl_gen)
    # count = 0
    # ltl.traverse(length)
    # if count > size_ltl: continue
    # if count < size_ltl: continue
    with open(f'./ltl/ltl{i}.txt', 'w') as file:
        file.write(str(ltl))
    csp, yaml = ltl2csp_rml.ltl2csp(str(ltl), f'csp{i}.csp')
    with open(f'./csp/csp{i}.csp', 'w') as file:
        file.write(str(csp))
    with open(f'./csp/csp{i}.yaml', 'w') as file:
        file.write(str(yaml))
    with open(f'./rml/rml{i}.rml', 'w') as file:
        file.write(str(ltl2csp_rml.ltl2rml(str(ltl))))
    i += 1
    if i % S == 0:
        size_ltl += 2
        ltl_gen = spot.randltl(list(string.ascii_lowercase), tree_size=size_ltl)
