def print_usage():
    print('flow-viewer.py <FLOW FILE> \n   -h, --help : display help\n   -s, --start_state <START-STATE> : add start state for BFS based search'\
          '\n   -m, --method_vals <METHOD_VALUES> : comma separated list of predefined outputs of methods'\
          '\n   -i, --initialize <VARIABLE VALUES> : comma seperated list of initial variable values. Useful when value of variable cannot be infered from flow file'\
          '\n   -e, --external <EXTERNAL NODES> : comma separated list of external nodes'\
          '\n   -g, --goal_state <GOAL_STATE> : only shows paths which include this state')