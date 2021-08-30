import sys

from constants import START_STATE_COLOR, STATE_COLORS, ALL_STATES, EXTERNAL_STATE_COLOR
from scope import Context


class GraphCreator:
    def __init__(self, flowdom, track_vars, config):
        self.flowdom = flowdom
        self.track_vars = track_vars
        self.config = config
        self.scanned_nodes = 0

        print(f"{track_vars=} {config=}")
        self.load_graph()

    def make_graph(self, *args, **kwargs):
        raise Exception("call to base class")

    def load_graph(self):
        self.initial_context = Context(self.track_vars)
        if 'initial_vals' in self.config:
            print("Initializing variables with following : " + self.config['initial_vals'])
            try:
                for initial_val in self.config['initial_vals'].split(','):
                    self.initial_context.set_var(initial_val.split(":")[0], [initial_val.split(":")[1]])
            except:
                raise Exception("error while parsing variable overrides")

        self.external_nodes = set()
        if "external_states" in self.config:
            print("Using following external nodes : " + self.config["external_states"])
            try:
                self.external_nodes = set(self.config["external_states"].split(","))
            except:
                raise Exception("error while parsing external nodes")

        self.method_vals = {}
        if 'method_vals' in self.config:
            print("Using following possible returns value for specified methods : " + self.config['method_vals'])
            try:
                self.method_vals = {meth_val.split(':')[0]: meth_val.split(':')[1].split('|')
                                    for meth_val in self.config['method_vals'].split(',')}
            except:
                raise Exception("error while decoding predefined method values")

        # start state not specified, check if specified as flow attribute
        self.start_state = self.config.get("start_state", None)
        if not self.start_state:
            print("Start state not specified, scanning for start state...")
            self.start_state = self.flowdom.getElementsByTagName("flow")[0].getAttribute("start-state")
        if not self.start_state:
            print("Could not find start state, please specify using --start_state <START-STATE>")
            raise Exception("could not find start state")
        print("start_state = " + self.start_state)

        # scan on-start for variable self.configuration
        on_start_node = self.flowdom.getElementsByTagName('on-start')
        if on_start_node:
            print("Parsing on-start...")
            self.parse_non_transitions_node(on_start_node[0], self.initial_context)

        # for speed build map from state id to dom objects
        # and create map from state id to state type for coloring
        # all global states are end states
        self.stateDOM_map = {}
        self.end_states = self.external_nodes.copy()
        self.nodes_colors_map = {}
        for state_type in ALL_STATES:
            state_nodes = self.flowdom.getElementsByTagName(state_type)
            for state_node in state_nodes:
                state = state_node.getAttribute("id")
                self.stateDOM_map[state] = state_node
                self.nodes_colors_map[state] = STATE_COLORS[state_type]
                if state_type == "end-state":
                    self.end_states.add(state)
        self.nodes_colors_map[self.start_state] = START_STATE_COLOR

        for external_node in self.external_nodes:
            self.stateDOM_map[external_node] = None
            self.nodes_colors_map[external_node] = EXTERNAL_STATE_COLOR

    #
    #   will go beyond first layer
    #
    def parse_non_transitions_node(self, node, context: Context):
        for evaluate_node in node.getElementsByTagName('evaluate'):
            self.handle_evaluate_node(evaluate_node, context)
        for set_node in node.getElementsByTagName('set'):
            self.handle_set_node(set_node, context)

    def handle_evaluate_node(self, evaluate_node, context: Context):
        var_name = evaluate_node.getAttribute("result")
        method_call = evaluate_node.getAttribute("expression")
        if context.contains_var(var_name):
            if method_call in self.method_vals:
                context.set_var(var_name, self.method_vals[method_call])
            else:
                raise Exception(
                    "output values of \'" + method_call + "\' not defined, please define using --method_vals <METHOD_VALUES>")

    def handle_set_node(self, set_node, context: Context):
        var_name = set_node.getAttribute("name")
        val = set_node.getAttribute("value")
        if context.contains_var(var_name):
            if "(" in val:
                if val in self.method_vals:
                    context.set_var(var_name, self.method_vals[val])
                else:
                    raise Exception(
                        "output values of \'" + val + "\' not defined, please define using --method_vals <METHOD_VALUES>")
            else:
                context.set_var(var_name, [val])

    def update_scanned_nodes(self):
        self.scanned_nodes += 1
        print(f"\r {self.scanned_nodes} nodes scanned", end='')
        sys.stdout.flush()
    