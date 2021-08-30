#!/usr/bin/python

import sys
from xml.dom import minidom
from sysarg_parser import parseargs
from graph_renderer import render
from graph_creator import make_graph_no_BFS, make_graph_BFS
from post_operations import map_to_state
from common import print_usage
from creator.impl import GraphCreatorBFS


def main(argv):
    try:
        flowfile, config = parseargs(argv)
    except Exception as e:
        print_usage()
        raise e
    flowdom = minidom.parse(flowfile)

    # try with tracking Scope variables
    print("Building directed graph without keeping track of scope variables...")
    G, colors, track_vars = make_graph_no_BFS(flowdom)

    # some Scope variables must be tracked, use BFS algorithm
    if track_vars or True:
        print("Detected scope variables that must be tracked. Building graph using BFS algorithm...")
        # G, colors = make_graph_BFS(flowdom, track_vars, config)
        creator = GraphCreatorBFS(flowdom, track_vars, config)
        G, colors = creator.make_graph()

    if "goal_state" in config:
        map_to_state(G, config["goal_state"])

    print("Rendering graph...")
    render(G, colors)

if __name__ == "__main__":
    main(sys.argv)

