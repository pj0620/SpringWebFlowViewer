import getopt
import sys

def print_usage():
    print('flow-viewer.py <FLOW FILE> \n   -h, --help : display help\n   -s, --start_state <START-STATE> : add start state for BFS based search'\
          '\n   -m, --method_vals <METHOD_VALUES> : comma separated list of predefined outputs of methods')

def parseargs(argv):
    try:
        flowfile = argv[1]
    except IndexError:
        raise Exception("flow file not specified")

    if len(argv) < 3:
        return flowfile, {}

    config = {}
    try:
        opts, args = getopt.getopt(argv[2:],"hs:m:",["help","start_state=","method_vals="])
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

    print(config)

    return flowfile, config
