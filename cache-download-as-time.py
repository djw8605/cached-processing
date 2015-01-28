#!/usr/bin/python

import optparse
import os
import re
from multiprocessing import Pool
import datetime
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import numpy
import time

def parse_file(filename):

    print "Examining %s" % filename
    
    # Fri Jan 23 16:40:18 CST 2015
    start_re = re.compile(".*start time = (.*)$")
    end_re = re.compile(".*end time = (.*)$")

    f = open(filename, 'r')
    for line in f:
        start_match = start_re.search(line)
        if start_match:
            start_time = start_match.group(1)
            print "started at %s" % start_time
        end_match = end_re.search(line)
        if end_match:
            end_time = end_match.group(1)
            print "Ended at %s" % end_time
            break

    # Sat Jan 24 16:02:37 CST 2015
    time_format = "%a %b %d %H:%M:%S %Z %Y"
    start_fmt = datetime.datetime.strptime(start_time, time_format)
    end_fmt = datetime.datetime.strptime(end_time, time_format)

    difference = end_fmt - start_fmt
    seconds = (difference.microseconds + (difference.seconds + difference.days * 24 * 3600) * 10**6) / 10**6
    print "Total seconds = %i" % seconds

    return (time.mktime(start_fmt.timetuple()), seconds)
    



def add_options(parser):

    parser.add_option("-p", "--procs", dest="processes", type="int",
                                  help="Number of processes to start", default=2)




def main():
    parser = optparse.OptionParser()
    add_options(parser)

    (options, args) = parser.parse_args()

    output_file = args[0]
    args.pop(0)

    graph = {}

    pool = Pool(processes = options.processes)
    results = pool.map(parse_file, args)


    print results
    x = []
    y = []

    for (time, duration) in results:
        x.append(time)
        y.append(duration)


    plt.scatter(x, y)
    plt.axis([numpy.amin(x), 13000+1.42213e9, 0, numpy.amax(y)])

    plt.xlabel("Time")
    plt.ylabel("Download Time")
    plt.title("Download duration over time of the workflow")

    plt.savefig("scatter_of_downloadtimes.png")



    #for (graph_result, map_result) in results:
    #    graph = dict(graph.items() + graph_result.items())
    #    map_dict = merge_dols(map_dict, map_result)


    #print map_dict
    #print "---------------------"
    #print graph

    #for file in args:
    #  parse_file(file, graph)

    #output_dot(output_file, graph)
    #print graph


if __name__ == "__main__":
    main()





