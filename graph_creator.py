import copy
import xml
from constants import ALL_STATES, STATE_COLORS, START_STATE_COLOR, EXTERNAL_STATE_COLOR
import networkx as nx
from scope import Context
import sys

scanned_nodes = 0
nodes_contexts_set = set()

def make_graph_BFS(flowdom, track_vars, config):
    context = Context(track_vars)
    if 'initial_vals' in config:
        print("Initializing variables with following : " + config['initial_vals'])
        try:
            for initial_val in config['initial_vals'].split(','):
                context.set_var(initial_val.split(":")[0], [initial_val.split(":")[1]])
        except:
            raise Exception("error while parsing variable overrides")

    external_nodes = set()
    if "external_states" in config:
        print("Using following external nodes : " + config["external_states"])
        try:
            external_nodes = set(config["external_states"].split(","))
        except:
            raise Exception("error while parsing external nodes")

    method_vals = {}
    if 'method_vals' in config:
        print("Using following possible returns value for specified methods : " + config['method_vals'])
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
    # and create map from state id to state type for coloring
    stateDOM_map = {}
    end_states = set()
    nodes_colors_map = {}
    for state_type in ALL_STATES:
        state_nodes = flowdom.getElementsByTagName(state_type)
        for state_node in state_nodes:
            state = state_node.getAttribute("id")
            stateDOM_map[state] = state_node
            nodes_colors_map[state] = STATE_COLORS[state_type]
            if state_type == "end-state":
                end_states.add(state)
    nodes_colors_map[start_state] = START_STATE_COLOR

    for external_node in external_nodes:
        stateDOM_map[external_node] = None
        nodes_colors_map[external_node] = EXTERNAL_STATE_COLOR

    print("Mapping flow file...")
    edges = set()
    visited = set()
    scanDomBFS(start_state, visited, context, edges, stateDOM_map, end_states, method_vals)

    # needed to add new line after scanned nodes message
    print("")

    print("Creating graph from results of scan...")
    G = nx.DiGraph()
    G.add_edges_from(edges)
    colors = [nodes_colors_map[node] for node in G.nodes()]
    # colors = ["blue"] * len(G.nodes)

    return G, colors


def scanDomBFS(cur, visited, context: Context, edges, stateDOM_map, end_states, method_vals):
    # break if we have already scanned this node with this context
    global nodes_contexts_set
    if (cur, context) in nodes_contexts_set:
        return
    else:
        nodes_contexts_set.add((cur,context))

    update_scanned_nodes()

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
            handle_set_node(child, context, method_vals)
        elif child.localName == "transition":
            next_state = child.getAttribute("to")
            if next_state:
                next_states.append(next_state)
        elif child.localName == "if":
            next_state_then = child.getAttribute("then")
            if next_state_then:
                next_states.append(next_state_then)
            next_state_else = child.getAttribute("else")
            if next_state_else:
                next_states.append(next_state_else)
        else:
            parse_non_transitions_node(child, context, method_vals)

    for next_state in next_states:
        # if next state is a scope variable, branch with every possibility
        if "#{" in next_state:
            fixed_next_state = next_state.replace("#{", "").replace("}", "")
            possible_next_states = context.get_vals(fixed_next_state)
            if not possible_next_states:
                raise Exception(f"value of {fixed_next_state} cannot be inferred from flow file, please initialize "
                                f"this variable using using --initialize <VARIABLE VALUES>")
            for possible_next_state in possible_next_states:
                if possible_next_state == "null":
                    continue
                edges.add((cur, possible_next_state))
                new_context = copy.deepcopy(context)
                new_context.set_var(fixed_next_state, [possible_next_state])
                new_visited = copy.deepcopy(visited)
                try:
                    dom = stateDOM_map[possible_next_state]
                except:
                    raise Exception(f"unknown state '{possible_next_state}', if this is an external state please specify it "
                                    f"using --external <EXTERNAL NODES>")
                if not dom:
                    continue
                if dom.childNodes:
                    parse_non_transitions_node(dom, new_context, method_vals)
                scanDomBFS(possible_next_state, new_visited, new_context, edges, stateDOM_map, end_states, method_vals)

        # otherwise continue to next state
        else:
            if next_state in visited:
                continue
            edges.add((cur, next_state))
            new_visited = copy.deepcopy(visited)
            new_context = copy.deepcopy(context)
            try:
                dom = stateDOM_map[next_state]
            except:
                raise Exception(f"unknown state '{next_state}', if this is an external state please specify it using "
                                f"--external <EXTERNAL NODES>")
            if not dom:
                continue
            if dom.childNodes:
                parse_non_transitions_node(dom, new_context, method_vals)
            scanDomBFS(next_state, new_visited, new_context, edges, stateDOM_map, end_states, method_vals)


def make_graph_no_BFS(flowdom):
    nodes_states_map = {}
    edges = set()
    track_vars = []
    for state in ALL_STATES:
        scanDom(flowdom, state, edges, nodes_states_map, track_vars)

    G = nx.DiGraph()
    G.add_edges_from(edges)
    colors = None
    if not track_vars:
        colors = [STATE_COLORS[nodes_states_map[node]] for node in G.nodes()]

    return G, colors, track_vars


# scans minidom node for states, and edges
#  - edges appended to provided list
#  - nodes_state_map[state_id] = state_type
#  - track_vars -> list of vars that must be tracked for building graph
def scanDom(flowdom, stateName, edges, nodes_states_map, track_vars):
    stateNodes = flowdom.getElementsByTagName(stateName)

    def add_edge(state, next_state):
        if next_state:
            edges.add((state, next_state))
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
def parse_non_transitions_node(node, context: Context, method_vals):
    for evaluate_node in node.getElementsByTagName('evaluate'):
        handle_evaluate_node(evaluate_node, context, method_vals)
    for set_node in node.getElementsByTagName('set'):
        handle_set_node(set_node, context, method_vals)


def handle_evaluate_node(evaluate_node, context: Context, method_vals):
    var_name = evaluate_node.getAttribute("result")
    method_call = evaluate_node.getAttribute("expression")
    if context.contains_var(var_name):
        if method_call in method_vals:
            context.set_var(var_name, method_vals[method_call])
        else:
            raise Exception(
                "output values of \'" + method_call + "\' not defined, please define using --method_vals <METHOD_VALUES>")


def handle_set_node(set_node, context: Context, method_vals):
    var_name = set_node.getAttribute("name")
    val = set_node.getAttribute("value")
    if context.contains_var(var_name):
        if "(" in val:
            if val in method_vals:
                context.set_var(var_name, method_vals[val])
            else:
                raise Exception(
                    "output values of \'" + val + "\' not defined, please define using --method_vals <METHOD_VALUES>")
        else:
            context.set_var(var_name, [val])


def update_scanned_nodes():
    global scanned_nodes
    scanned_nodes += 1
    print(f"\r {scanned_nodes} nodes scanned", end='')
    sys.stdout.flush()