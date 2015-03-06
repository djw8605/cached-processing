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
from parse_file import parse_file


def add_options(parser):

    parser.add_option("-p", "--procs", dest="processes", type="int",
                                  help="Number of processes to start", default=2)




def main():
    parser = optparse.OptionParser()
    add_options(parser)

    (options, args) = parser.parse_args()



    pool = Pool(processes = options.processes)
    results = pool.map(parse_file, args)

    # Make the different cache modes
    total_results = [ [], [], [] ]

    for result in results:
        if result["mode"] == "cached":
            total_results[0].append(result["duration"])
        elif result["mode"] == "parent":
            total_results[1].append(result["duration"])
        elif result["mode"] == "child":
            total_results[2].append(result["duration"])


    #print results

    n, bins, patches = plt.hist(total_results, 25, alpha=0.75, stacked=True, label=['Cached', 'Parent', 'Children'])
    print bins
    print n
    l = plt.plot(bins)

    plt.axis([0, numpy.amax(bins), 0, numpy.amax(n)])
    plt.xlabel("Download Duration (s)")
    plt.ylabel("Number of instances")
    plt.title("Histogram of number of instances of download times")
    plt.legend()

    plt.savefig("modes_vs_downloadtimes.png")



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





