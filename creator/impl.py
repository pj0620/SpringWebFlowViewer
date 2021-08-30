import copy
import xml

import networkx as nx

from creator.base import GraphCreator
from scope import Context


class GraphCreatorBFS(GraphCreator):
    def __init__(self, flowdom, track_vars, config):
        super().__init__(flowdom, track_vars, config)

    def make_graph(self):
        print("Mapping flow file...")
        edges = set()
        visited = set()
        self.nodes_contexts_set = set()
        print(f"{self.start_state=} {self.initial_context=}")
        self.scanDomBFS(self.start_state, visited, self.initial_context, edges)

        # needed to add new line after scanned nodes message
        print("")

        print("Creating graph from results of scan...")
        G = nx.DiGraph()
        G.add_edges_from(edges)
        colors = [self.nodes_colors_map[node] for node in G.nodes()]
        # colors = ["blue"] * len(G.nodes)

        return G, colors

    def scanDomBFS(self, cur, visited, context: Context, edges):
        print(f"{cur=} {visited=} {context=}")

        # break if we have already scanned this node with this context
        if (cur, context) in self.nodes_contexts_set:
            return
        else:
            self.nodes_contexts_set.add((cur, context))

        # update_scanned_nodes()

        if cur in self.end_states or cur in visited:
            return

        visited.add(cur)

        next_states = []
        for child in self.stateDOM_map[cur].childNodes:
            if type(child) != xml.dom.minidom.Element:
                continue

            if child.localName == 'evaluate':
                self.handle_evaluate_node(child, context)
            elif child.localName == 'set':
                self.handle_set_node(child, context)
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
                self.parse_non_transitions_node(child, context)

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
                        dom = self.stateDOM_map[possible_next_state]
                    except:
                        raise Exception(
                            f"unknown state '{possible_next_state}', if this is an external state please specify it "
                            f"using --external <EXTERNAL NODES>")
                    if not dom:
                        continue
                    if dom.childNodes:
                        self.parse_non_transitions_node(dom, new_context)
                    self.scanDomBFS(possible_next_state, new_visited, new_context, edges)

            # otherwise continue to next state
            else:
                edges.add((cur, next_state))
                new_visited = copy.deepcopy(visited)
                new_context = copy.deepcopy(context)
                try:
                    dom = self.stateDOM_map[next_state]
                except:
                    raise Exception(
                        f"unknown state '{next_state}', if this is an external state please specify it using "
                        f"--external <EXTERNAL NODES>")
                if not dom:
                    continue
                if dom.childNodes:
                    self.parse_non_transitions_node(dom, new_context)
                self.scanDomBFS(next_state, new_visited, new_context, edges)

