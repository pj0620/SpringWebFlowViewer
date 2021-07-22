#!/usr/bin/python

import sys, getopt
from xml.dom import minidom
from sysarg_parser import parseargs
from graph_renderer import render
from graph_creator import make_graph_no_BFS, make_graph_BFS


def print_usage():
    print('flow-viewer.py <FLOW FILE> \n   -h, --help : display help\n   -s, --start_state <START-STATE> : add start state for BFS based search'\
          '\n   -m, --method_vals <METHOD_VALUES> : comma separated list of predefined outputs of methods'\
          '\n   -i, --initialize <VARIABLE VALUES> : comma seperated list of initial variable values. Useful when value of variable cannot be infered from flow file'\
          '\n   -e, --external <EXTERNAL NODES> : comma separated list of external nodes')


def main(argv):
    try:
        flowfile, config = parseargs(argv)
    except Exception as e:
        print(e)
        print_usage()
        sys.exit(2)
    flowdom = minidom.parse(flowfile)

    # try with tracking Scope variables
    print("Building directed graph without keeping track of scope variables...")
    G, colors, track_vars = make_graph_no_BFS(flowdom)

    # some Scope variables must be tracked, use BFS algorithm
    if track_vars:
        print("Detected scope variables that must be tracked. Building graph using BFS algorithm...")
        G, colors = make_graph_BFS(flowdom, track_vars, config)

    print("Rendering graph...")
    render(G, colors)

if __name__ == "__main__":
    main(sys.argv)

