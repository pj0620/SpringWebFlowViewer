def parseargs(argv):
    try:
        flowfile = argv[1]
    except IndexError:
        raise Exception("flow file not specified")

    if len(argv) != 2:
        raise Exception("too many arguments specified")

    config = {}
    # try:
    #     opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    # except getopt.GetoptError:
    #     print_usage()
    #     sys.exit(2)
    # for opt, arg in opts:
    #    if opt == '-h':
    #       print_usage()
    #       sys.exit()
    #    elif opt in ("-i", "--ifile"):
    #       inputfile = arg
    #    elif opt in ("-o", "--ofile"):
    #       outputfile = arg

    return flowfile, config
