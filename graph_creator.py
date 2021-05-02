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
    on_start_node = flowdom.getElementsByTagName('on-start')
    if on_start_node:
        print("Parsing on-start...")
        parse_non_transitions_node(on_start_node[0], context, method_vals)

    # for speed build map from state id to dom objects
    stateDOM_map = {}
    end_states = set()
    for state_name in ALL_STATES:
        state_nodes = flowdom.getElementsByTagName(state_name)
        for state_node in state_nodes:
            state = state_node.getAttribute("id")
            stateDOM_map[state] = state_node
            if state_name == "end-state":
                end_states.add(state_name)

    print(f"context = {context}")

    nodes_states_map = {}
    edges = []
    visited = set()
    scanDomBFS(start_state, visited, context, edges, nodes_states_map, stateDOM_map, end_states, method_vals)

    print(edges)

    G = nx.DiGraph()
    G.add_edges_from(edges)
    # colors = [STATE_COLORS[nodes_states_map[node]] for node in G.nodes()]
    colors = ["blue"] * len(G.nodes)

    return G, colors


def scanDomBFS(cur, visited, context, edges, nodes_state_map, stateDOM_map, end_states, method_vals):
    print(f"{cur} -> {visited}")

    if cur in end_states or cur in visited:
        return

    visited.add(cur)

    next_states = []
    for child in stateDOM_map[cur].childNodes:
        if type(child) != xml.dom.minidom.Element:
            continue

        if child.localName == 'evaluate':
            handle_evaluate_node(child, context, method_vals)
        elif child.localName == 'set':
            handle_set_node(child, context)
        elif child.localName == "transition":
            next_state = child.getAttribute("to")
            if next_state:
                next_states.append(next_state)
        else:
            parse_non_transitions_node(child, context, method_vals)

    for next_state in next_states:
        # if next state is a scope variable, branch with every possibility
        if "#{" in next_state:
            fixed_next_state = next_state.replace("#{", "").replace("}", "")
            possible_next_states = context.getVar(fixed_next_state).get_vals()
            if not possible_next_states:
                raise Exception(f"value of {fixed_next_state} cannot be inferred from flow file")
            for possible_next_state in possible_next_states:
                edges.append((cur, possible_next_state))
                new_context = copy.deepcopy(context)
                new_context.getVar(fixed_next_state).set_vals([possible_next_state])
                new_visited = copy.deepcopy(visited)
                new_visited.add(possible_next_state)
                if stateDOM_map[possible_next_state].childNodes:
                    parse_non_transitions_node(stateDOM_map[possible_next_state], new_context, method_vals)
                scanDomBFS(possible_next_state, new_visited, new_context, edges, nodes_state_map, stateDOM_map,
                           end_states, method_vals)

        # otherwise continue to next state
        else:
            if next_state in visited:
                continue
            edges.append((cur, next_state))
            new_visited = copy.deepcopy(visited)
            new_visited.add(next_state)
            new_context = copy.deepcopy(context)
            if stateDOM_map[next_state].childNodes:
                parse_non_transitions_node(stateDOM_map[next_state], new_context, method_vals)
            scanDomBFS(next_state, new_visited, new_context, edges, nodes_state_map, stateDOM_map, end_states,
                       method_vals)


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

#
#   will go beyond first layer
#
def parse_non_transitions_node(node, context, method_vals):
    for evaluate_node in node.getElementsByTagName('evaluate'):
        handle_evaluate_node(evaluate_node, context, method_vals)
    for set_node in node.getElementsByTagName('set'):
        handle_set_node(set_node, context)

def handle_evaluate_node(evaluate_node, context, method_vals):
    var_name = evaluate_node.getAttribute("result")
    method_call = evaluate_node.getAttribute("expression")
    if context.containsVar(var_name):
        if method_call in method_vals:
            context.getVar(var_name).set_vals(method_vals[method_call])
        else:
            raise Exception(
                "output values of \'" + method_call + "\' not defined, please define using --method_vals <METHOD_VALUES>")

def handle_set_node(set_node, context):
    var_name = set_node.getAttribute("name")
    if context.containsVar(var_name):
        context.getVar(var_name).set_vals([set_node.getAttribute("value")])