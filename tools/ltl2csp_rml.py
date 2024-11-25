import sys
import argparse
import spot
import buddy

# Function to convert an LTL formula into a CSP model
def ltl2csp(ltl, name=None):
    csp = 'channel '  # Start the CSP model with the 'channel' declaration
    # Translate the LTL formula to a monitor automaton using Spot
    monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
    print(monitor.to_str())
    l = []  # Initialize a list to hold atomic propositions (APs)
    
    # Collect all atomic propositions (APs) used in the monitor
    for ap in monitor.ap():
        l.append(f'{ap}')
    
    # Add APs to the CSP channel declaration
    csp += ', '.join(l) + '\n\n'
    channels = ', '.join(l)
    
    transitions = {}  # Dictionary to store state transitions
    
    # Iterate over all states in the monitor
    for s in range(0, monitor.num_states()):
        transitions[str(s)] = {}  # Initialize transition mapping for the current state
        
        # Iterate over all transitions from the current state
        for t in monitor.out(s):
            for ap in monitor.ap():
                ap = str(ap)
                bdd = buddy.bddtrue  # Start with a true BDD (Boolean Decision Diagram)
                
                # Build a BDD for the current atomic proposition
                for ap1 in monitor.ap():
                    ap1 = str(ap1)
                    if ap == ap1:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_ithvar(p)
                    else:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_nithvar(p)
                
                # Check if the transition condition is consistent with the BDD
                if (t.cond & bdd) != buddy.bddfalse:
                    # Store the transition destination state for the current AP
                    transitions[str(s)][ap] = str(t.dst)
    
    # Build the CSP process model
    for s in transitions:
        csp += f'state{s} = \n'  # Start defining the state process
        l = []
        for ap in transitions[s]:
            # Add the transition logic for each atomic proposition
            l.append(f'{ap} -> state{transitions[s][ap]}')
        csp += '\n[]\n'.join(l)  # Join multiple transitions with non-deterministic choice
        csp += '\n\n'
    
    # Add main process and verification conditions to the CSP model
    csp += f'WCST = state{monitor.get_init_state_number()} -- Main Process, starts the recursion in state{monitor.get_init_state_number()}\n\n'
    csp += f'assert state{monitor.get_init_state_number()}; RUN(Events) :[deadlock free]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[deterministic]:\n'
    csp += f'assert state{monitor.get_init_state_number()} :[divergence free]:'
    
    if not name:
        name = 'random_csp.csp'

    yaml = f'''---
alphabet: [{channels}]
common_alphabet: [{channels}]
main_process: "state{monitor.get_init_state_number()}"
model: "{name}" 
trace_file: "log.txt" 
name: "random_csp"
mode: "strict"'''

    return csp, yaml  # Return the complete CSP model and Yaml config file

# Function to convert an LTL formula into an RML (Reactive Model Logic) model
def ltl2rml(ltl):
    rml = ''  # Initialize the RML string
    # Translate the LTL formula to a monitor automaton using Spot
    monitor = spot.translate(ltl, 'monitor', 'det', 'complete')
    l = []  # List to store atomic propositions
    
    # Build event matching rules for each atomic proposition
    for ap in monitor.ap():
        l.append(f'{ap} matches {{ event: \'{ap}\' }};')
    rml += '\n'.join(l) + '\n\n'  # Add the rules to the RML string
    
    transitions = {}  # Dictionary to store state transitions
    
    # Iterate over all states in the monitor
    for s in range(0, monitor.num_states()):
        transitions[str(s)] = {}  # Initialize transition mapping for the current state
        
        # Iterate over all transitions from the current state
        for t in monitor.out(s):
            for ap in monitor.ap():
                ap = str(ap)
                bdd = buddy.bddtrue  # Start with a true BDD
                
                # Build a BDD for the current atomic proposition
                for ap1 in monitor.ap():
                    ap1 = str(ap1)
                    if ap == ap1:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_ithvar(p)
                    else:
                        p = monitor.register_ap(ap1)
                        bdd = bdd & buddy.bdd_nithvar(p)
                
                # Check if the transition condition is consistent with the BDD
                if (t.cond & bdd) != buddy.bddfalse:
                    # Store the transition destination state for the current AP
                    transitions[str(s)][ap] = str(t.dst)
    
    # Build the RML process model
    for s in transitions:
        if s == str(monitor.get_init_state_number()):
            rml += 'Main = '  # Main process corresponds to the initial state
        else:
            rml += f'state{s} = '  # Define other states
        
        l = []
        for ap in transitions[s]:
            # Add the transition logic for each atomic proposition
            if str(monitor.get_init_state_number()) == transitions[s][ap]:
                l.append(f'{ap} Main')
            else:
                l.append(f'{ap} state{transitions[s][ap]}')
        
        rml += ' \/ '.join(l)  # Join multiple transitions with choice operator
        rml += ';\n'
    
    return rml  # Return the complete RML model

# Main function to execute the script
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert an LTL formula into CSP and RML models.')
    parser.add_argument('ltl', help='The LTL formula to be converted.')
    parser.add_argument('--csp-output', default='monitor.csp', help='Output file for the CSP model (default: monitor.csp)')
    parser.add_argument('--rml-output', default='monitor.rml', help='Output file for the RML model (default: monitor.rml)')
    
    # Parse the command line arguments
    args = parser.parse_args()

    csp, yaml = ltl2csp(args.ltl, args.csp_output)

    # Write the CSP model to a file
    with open(args.csp_output, 'w') as file:
        file.write(csp)
    with open(args.csp_output.replace('.csp', '.yaml'), 'w') as file:
        file.write(yaml)
     
    # Write the RML model to a file
    with open(args.rml_output, 'w') as file:
        file.write(ltl2rml(args.ltl))

    print(f"CSP model written to {args.csp_output}")
    print(f"RML model written to {args.rml_output}")

# Entry point of the script
if __name__ == '__main__':
    main()
