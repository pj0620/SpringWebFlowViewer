from constants import ALL_STATES, STATE_COLORS
import networkx as nx

def make_graph(flowdom):
    nodes_states_map = {}
    edges = []
    for state in ALL_STATES:
        scanDom(flowdom, state, edges, nodes_states_map)

    G = nx.DiGraph()
    G.add_edges_from(edges)
    colors = [STATE_COLORS[nodes_states_map[node]] for node in G.nodes()]

    return G, colors

# scans minidom node for states, and edges
# edges appended to provided list
#
# returns
#   node -> nodes found [list(str)]
def scanDom(flowdom, stateName, edges, nodes_states_map):
    stateNodes = flowdom.getElementsByTagName(stateName)

    for stateNode in stateNodes:
        # store found state
        state = stateNode.getAttribute("id")
        nodes_states_map[state] = stateName

        # store edges
        for transitionNode in stateNode.getElementsByTagName('transition'):
            next_state = transitionNode.getAttribute("to")
            if next_state:
                edges.append((state, next_state))
        for transitionNode in stateNode.getElementsByTagName('if'):
            next_state_then = transitionNode.getAttribute("then")
            if next_state_then:
                edges.append((state, next_state_then))
            next_state_else = transitionNode.getAttribute("else")
            if next_state_else:
                edges.append((state, next_state_else))
