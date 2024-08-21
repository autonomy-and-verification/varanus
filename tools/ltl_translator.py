import sys
import string
import spot
import buddy
import os
sys.path.insert(0, os.path.abspath('../varanus-python'))
from csp_state_machine import *

def ltl2cspstatemachine(ltl):
    machine = CSPStateMachine()
    csp = 'channel '
    monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
    l = []
    for ap in monitor.ap():
        l.append(f'{ap}')
        print(ap)
        machine.add_letter_to_alphabet(ap)
    csp += ', '.join(l) + '\n\n'
    transitions = {}
    for s in range(0, monitor.num_states()):
        transitions[str(s)] = {}
        for t in monitor.out(s):
            for ap in monitor.ap():
                ap = str(ap)
                bdd = buddy.bddtrue
                for ap1 in monitor.ap():
                    ap1 = str(ap1)
                    if ap == ap1:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_ithvar(p)
                    else:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_nithvar(p)
                if (t.cond & bdd) != buddy.bddfalse:
                    transitions[str(s)][ap] = str(t.dst)
    print(str(transitions))
    for s in transitions:
        csp += f'state{s} = \n'
        print(s)
        machine.add_destination(s)
        l = []
        for ap in transitions[s]:
            l.append(f'{ap} -> state{transitions[s][ap]}')
            machine.add_transition_by_name(ap, s, transitions[s][ap])
        csp += '\n[]\n'.join(l)
        csp += '\n\n'
    csp += f'WCST = state{monitor.get_init_state_number()} -- Main Process, starts the recursion in state{monitor.get_init_state_number()}\n\n'
    csp += f'assert state{monitor.get_init_state_number()}; RUN(Events) :[deadlock free]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[deterministic]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[divergence free]:'
    return machine

def ltl2csp(ltl):
    csp = 'channel '
    monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
    l = []
    for ap in monitor.ap():
        l.append(f'{ap}')
    csp += ', '.join(l) + '\n\n'
    transitions = {}
    for s in range(0, monitor.num_states()):
        transitions[str(s)] = {}
        for t in monitor.out(s):
            for ap in monitor.ap():
                ap = str(ap)
                bdd = buddy.bddtrue
                for ap1 in monitor.ap():
                    ap1 = str(ap1)
                    if ap == ap1:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_ithvar(p)
                    else:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_nithvar(p)
                if (t.cond & bdd) != buddy.bddfalse:
                    transitions[str(s)][ap] = str(t.dst)
    print(str(transitions))
    for s in transitions:
        csp += f'state{s} = \n'
        l = []
        for ap in transitions[s]:
            l.append(f'{ap} -> state{transitions[s][ap]}')
        csp += '\n[]\n'.join(l)
        csp += '\n\n'
    csp += f'WCST = state{monitor.get_init_state_number()} -- Main Process, starts the recursion in state{monitor.get_init_state_number()}\n\n'
    csp += f'assert state{monitor.get_init_state_number()}; RUN(Events) :[deadlock free]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[deterministic]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[divergence free]:'
    return csp

def ltl2rml(ltl):
    rml = ''
    monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
    l = []
    for ap in monitor.ap():
        l.append(f'{ap} matches {{ event: \'{ap}\' }};')
    rml += '\n'.join(l) + '\n\n'
    transitions = {}
    for s in range(0, monitor.num_states()):
        transitions[str(s)] = {}
        for t in monitor.out(s):
            for ap in monitor.ap():
                ap = str(ap)
                bdd = buddy.bddtrue
                for ap1 in monitor.ap():
                    ap1 = str(ap1)
                    if ap == ap1:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_ithvar(p)
                    else:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_nithvar(p)
                if (t.cond & bdd) != buddy.bddfalse:
                    transitions[str(s)][ap] = str(t.dst)
    print(str(transitions))
    for s in transitions:
        if s == str(monitor.get_init_state_number()):
            rml += 'Main = '
        else:
            rml += f'state{s} = '
        l = []
        for ap in transitions[s]:
            if str(monitor.get_init_state_number()) == transitions[s][ap]:
                l.append(f'{ap} Main')
            else:
                l.append(f'{ap} state{transitions[s][ap]}')

        rml += ' \/ '.join(l)
        rml += ';\n'
    return rml

def main(args):
    ltl = args[1]
    #with open('../evaluation/monitor.csp', 'w') as file:
    #    file.write(ltl2csp(ltl))
   # with open('../evaluation/monitor.rml', 'w') as file:
    #    file.write(ltl2rml(ltl))
    machine = ltl2cspstatemachine(ltl)
    print(str(machine))

    for s in machine.destinations.values():
        for trans in s.transitions:
            print(trans)

if __name__ == '__main__':
    main(sys.argv)