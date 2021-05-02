import copy
import xml
from constants import ALL_STATES, STATE_COLORS
import networkx as nx
from scope import Context

def make_graph_BFS(flowdom, track_vars, config):
    context = Context(track_vars)

    method_vals = {}
    if 'method_vals' in config:
        try:
            method_vals = {meth_val.split(':')[0]: meth_val.split(':')[1].split('|')
                                for meth_val in config['method_vals'].split(',')}
        except:
            raise Exception("error while decoding predefined method values")

    # start state not specified, check if specified as flow attribute
    start_state = config.get("start_state", None)
    if not start_state:
        print("Start state not specified, scanning for start state...")
        start_state = flowdom.getElementsByTagName("flow")[0].getAttribute("start-state")
    if not start_state:
        print("Could not find start state, please specify using --start_state <START-STATE>")
        raise Exception("could not find start state")
    print("start_state = " + start_state)

    # scan on-start for variable configuration
    on_start_node = flowdom.getElementsByTagName('on-start')[0]
    for evaluate_node in on_start_node.getElementsByTagName('evaluate'):
        handle_evaluate_node(evaluate_node, context, method_vals)
    for set_node in on_start_node.getElementsByTagName('set'):
        handle_set_node(set_node, context)

    # for speed build map from state id to dom objects
    stateDOM_map = {}
    for state_name in ALL_STATES:
        state_nodes = flowdom.getElementsByTagName(state_name)
        for state_node in state_nodes:
            state = state_node.getAttribute("id")
            stateDOM_map[state] = state_node

    nodes_states_map = {}
    edges = []
    queue = [start_state]
    scanDomBFS(queue, context, edges, nodes_states_map, stateDOM_map)

    return None, []

def scanDomBFS(queue, context, edges, nodes_state_map, stateDOM_map):
    cur = queue.pop(0)
    for child in stateDOM_map[cur].childNodes:
        if type(child) != xml.dom.minidom.Element:
            continue

        if child.localName is "transition":
            next_state_name = child.getAttribute("to")

            # if next state is a scope variable, branch with every possibility
            if "#{" in next_state_name:
                fixed_next_state = next_state_name.replace("#{", "").replace("}", "")
                possible_next_states = context.getVar(fixed_next_state).vals
                for possible_next_state in possible_next_states:
                    edges.append((cur, possible_next_state))
                    new_context = copy.deepcopy(context)
                    new_context.getVar(fixed_next_state).vals = [possible_next_state]
                    scanDomBFS(queue, new_context, edges, nodes_state_map, stateDOM_map)

            # otherwise coninue to next state
            else:
                edges.append((cur,next_state_name))
                scanDomBFS(queue, copy.deepcopy(context), edges, nodes_state_map, stateDOM_map)


def make_graph_no_BFS(flowdom):
    nodes_states_map = {}
    edges = []
    track_vars = []
    for state in ALL_STATES:
        scanDom(flowdom, state, edges, nodes_states_map, track_vars)

    G = nx.DiGraph()
    G.add_edges_from(edges)
    # colors = [STATE_COLORS[nodes_states_map[node]] for node in G.nodes()]
    colors = ["blue"]*len(G.nodes)

    return G, colors, track_vars

# scans minidom node for states, and edges
#  - edges appended to provided list
#  - nodes_state_map[state_id] = state_type
#  - track_vars -> list of vars that must be tracked for building graph
def scanDom(flowdom, stateName, edges, nodes_states_map, track_vars):
    stateNodes = flowdom.getElementsByTagName(stateName)

    def add_edge(state, next_state):
        if next_state:
            edges.append((state, next_state))
            if "#{" in next_state:
                track_vars.append(next_state.replace("#{", "").replace("}", ""))

    for stateNode in stateNodes:
        # store found state
        state = stateNode.getAttribute("id")
        nodes_states_map[state] = stateName

        # store edges
        for transitionNode in stateNode.getElementsByTagName('transition'):
            add_edge(state, transitionNode.getAttribute("to"))
        for transitionNode in stateNode.getElementsByTagName('if'):
            add_edge(state, transitionNode.getAttribute("then"))
            add_edge(state, transitionNode.getAttribute("else"))


def handle_evaluate_node(evaluate_node, context, method_vals):
    varName = evaluate_node.getAttribute("result")
    methodCall = evaluate_node.getAttribute("expression")
    if context.containsVar(varName):
        if methodCall in method_vals:
            context.getVar(varName).val = method_vals[methodCall]
        else:
            raise Exception(
                "output values of \'" + methodCall + "\' not defined, please define using --method_vals <METHOD_VALUES>")

def handle_set_node(set_node, context):
    varName = set_node.getAttribute("name")
    if context.containsVar(varName):
        context.getVar(varName).set(set_node.getAttribute("value"))