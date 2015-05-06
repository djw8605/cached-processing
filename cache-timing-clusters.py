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
import scipy.stats
import time

from parse_file import parse_file


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def add_options(parser):

    parser.add_option("-p", "--procs", dest="processes", type="int",
                                  help="Number of processes to start", default=2)




def main():
    parser = optparse.OptionParser()
    add_options(parser)

    (options, args) = parser.parse_args()

    filesize = int(args.pop(0))


    #output_file = args[0]
    #args.pop(0)

    #graph = {}

    pool = Pool(processes = options.processes)
    results = pool.map(parse_file, args)


    already_cached = []
    not_cached = []
    arrays = {}

    print "Number of jobs = %i" % len(results)

    for cache_info in results:
        cluster = cache_info["cluster"]
        if cluster not in arrays:
            arrays[cluster] = {}
        cur_cluster = arrays[cluster]


        if cache_info["mode"] not in cur_cluster:
            cur_cluster[cache_info["mode"]] = []
        cur_mode = cur_cluster[cache_info["mode"]]
            

        cur_mode.append(cache_info["duration"])

    sum_stagein = 0

    for cluster in arrays.keys():
        print "For %s" % cluster
        for mode in arrays[cluster].keys():
            cur_mode = arrays[cluster][mode]
            print mode + ": Number = %i" % (len(cur_mode))
            print mode + ": mean = %lf, median = %lf, std. dev = %lf, std. err = %lf" % ( numpy.mean(cur_mode), numpy.median(cur_mode), numpy.std(cur_mode), scipy.stats.sem(cur_mode))
            print mode + ": Total stagein = %i" % (numpy.sum(cur_mode))
            sum_stagein += numpy.sum(cur_mode)
            print mode + ": Speed = %s" % (sizeof_fmt(filesize / numpy.mean(cur_mode), suffix="B/s"))

    print "Total stagein = %i" % sum_stagein

    #print "Cached: mean = %lf, median = %lf" % (numpy.mean(already_cached), numpy.median(already_cached))
    #print "Not Cached: mean = %lf, median = %lf" % (numpy.mean(not_cached), numpy.median(not_cached))

    

    #print "Not Cached Speed: mean = %s" % (sizeof_fmt(filesize / numpy.mean(not_cached), suffix="B/s"))

    



    #plt.scatter(x, y)
    #plt.axis([numpy.amin(x), 13000+1.42213e9, 0, numpy.amax(y)])

    #plt.xlabel("Time")
    #plt.ylabel("Download Time")
    #plt.title("Download duration over time of the workflow")

    #plt.savefig("scatter_of_downloadtimes.png")



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





