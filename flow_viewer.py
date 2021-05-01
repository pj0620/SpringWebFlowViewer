#!/usr/bin/python

import sys, getopt
from xml.dom import minidom
from sysarg_parser import parseargs
from graph_renderer import render
from graph_creator import make_graph_no_BFS

def print_usage():
    print('flow-viewer.py <FLOW FILE>')


def main(argv):
    try:
        flowfile, config = parseargs(argv)
    except Exception:
        print_usage()
        sys.exit(2)
    flowdom = minidom.parse(flowfile)
    G, colors, track_vars = make_graph_no_BFS(flowdom)
    print(track_vars)
    render(G, colors)

if __name__ == "__main__":
    main(sys.argv)

