import getopt
import sys
from common import print_usage

def parseargs(argv):
    try:
        flowfile = argv[1]
    except IndexError:
        raise Exception("flow file not specified")

    if len(argv) < 3:
        return flowfile, {}

    config = {}
    opts, args = getopt.getopt(argv[2:],"hs:m:i:e:g:",["help","start_state=","method_vals=","initialize=","external=","goal_state="])

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
       elif opt in ("-g", "--goal_state"):
           config["goal_state"] = arg

    return flowfile, config
