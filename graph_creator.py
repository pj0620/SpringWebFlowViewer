from constants import ALL_STATES, STATE_COLORS
import networkx as nx

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
