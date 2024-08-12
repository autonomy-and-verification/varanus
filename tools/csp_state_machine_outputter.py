import pydot
import sys
import os
sys.path.insert(0, os.path.abspath('../varanus-python'))
from csp_state_machine import *

def state_machine_2_dot(csp_machine):
    graph = pydot.Dot("CSP Process", graph_type="digraph", bgcolor="grey")
    for state in csp_machine.states.values():
        graph.add_node(pydot.Node(state.name, shape="circle"))

        for transition in state.transitions.values():

            t_name = transition.name
            if t_name == Transition._TERMINATE:
                t_name = "Tick"
            graph.add_edge(pydot.Edge(state.name, transition.get_destination().name, label=t_name))

    graph.write_png("csp_graph.png")


def state_machine_2_dot_string(csp_machine):

    dot_string = "digraph CSPProcess{\nbgcolor = grey\n"

    for state in csp_machine.states.values():
        #graph.add_node(pydot.Node(state.name, shape="circle"))
        dot_string += str(state.name) + "[shape=circle]\n"

        for transition in state.transitions.values():

            t_name = transition.name
            if t_name == Transition._TERMINATE:
                t_name = "Tick"
            #graph.add_edge(pydot.Edge(state.name, transition.get_destination().name, label=t_name))
            dot_string += str(state.name) + " -> " + str(transition.get_destination().name) + " [label="+str(t_name)+"]\n"
    dot_string += "}"
    graphs = pydot.graph_from_dot_data(dot_string)
    graphs[0].write_png("csp_graph.png")



if __name__ == "__main__":
    """ Test the CSP State Machine"""

    machine = CSPStateMachine()

    csp_dict = {0: [("a",1)],1: [("b",2)], 2: [(Transition._TERMINATE, 3)], 3: [] }
    machine.load_from_dictionary(csp_dict)
    machine.start()
    print(str(machine.to_dictionary()))
    #state_machine_2_dot(machine)
    #state_machine_2_dot_string(machine)

    dot_string = machine.to_DOT()
    graphs = pydot.graph_from_dot_data(dot_string)
    graphs[0].write_png("csp_graph.png")
    print("Done")