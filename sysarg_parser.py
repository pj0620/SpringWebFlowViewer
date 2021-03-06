import getopt
import sys

def print_usage():
    print('flow-viewer.py <FLOW FILE> \n   -h, --help : display help\n   -s, --start_state <START-STATE> : add start state for BFS based search'\
          '\n   -m, --method_vals <METHOD_VALUES> : comma separated list of predefined outputs of methods'\
          '\n   -i, --initialize <VARIABLE VALUES> : comma seperated list of initial variable values. Useful when value of variable cannot be infered from flow file'\
          '\n   -e, --external <EXTERNAL NODES> : comma separated list of external nodes')


def parseargs(argv):
    try:
        flowfile = argv[1]
    except IndexError:
        raise Exception("flow file not specified")

    if len(argv) < 3:
        return flowfile, {}

    config = {}
    try:
        opts, args = getopt.getopt(argv[2:],"hs:m:i:e:",["help","start_state=","method_vals=","initialize=","external="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
       if opt in ("-h", "--help"):
          print_usage()
          sys.exit()
       elif opt in ("-s", "--start_state"):
          config["start_state"] = arg
       elif opt in ("-m", "--method_vals"):
          config["method_vals"] = arg
       elif opt in ("-i", "--initialize"):
          config["initial_vals"] = arg
       elif opt in ("-e", "--external"):
          config["external_states"] = arg

    return flowfile, config
