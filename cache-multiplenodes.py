#!/usr/bin/python

import optparse
import os
import re
from multiprocessing import Pool
import datetime
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy
import time

from parse_file import parse_file



def add_options(parser):

    parser.add_option("-p", "--procs", dest="processes", type="int",
                                  help="Number of processes to start", default=2)




def main():
    parser = optparse.OptionParser()
    add_options(parser)

    (options, args) = parser.parse_args()

    #output_file = args[0]
    #args.pop(0)

    #graph = {}

    pool = Pool(processes = options.processes)
    results = pool.map(parse_file, args)


    already_cached = []
    not_cached = []

    sorted_results = sorted(results, key=lambda cache: cache["host"])

    collection = []
    i = 0

    counter = 0
    while len(sorted_results) > 0:
        collection.append([])
        host = sorted_results[0]["host"]

        while len(sorted_results) > 0 and host == sorted_results[0]["host"]:
            #rectangle = plt.Rectangle((time.mktime(cache["starttime"].timetuple()), i*2), cache["duration"], 1.5)
            #plt.gca().add_patch(rectangle)
            collection[counter].append(sorted_results[0])
            sorted_results.pop(0)

        counter += 1 

    for i in range(len(collection)):
        host = collection[i]
        collection[i] = sorted(host, key=lambda cache: cache["starttime"])

    import math
    #unique_identifier_key = "_CONDOR_SLOT"
    unique_identifier_key = "slurm_jobid"

    for sorted_timeline in collection:
        plt.clf()
        plt.axes()
        counter = 0
        jobidmatch = {}
        max_time = 0
        host = sorted_timeline[0]["host"]
    
        
        for i in range(len(sorted_timeline)):
            cache = sorted_timeline[i]
            if cache[unique_identifier_key] not in jobidmatch:
                jobidmatch[cache[unique_identifier_key]] = counter
                counter+=2
    
            if cache["initialCached"]:
                color = 'green'
                label = "Cached"
            else:
                color = 'red'
                label = "UnCached"
            
            rectangle = plt.Rectangle((time.mktime(cache["starttime"].timetuple()), jobidmatch[cache[unique_identifier_key]]), cache["duration"], 1.5, color = color, label = label)
            max_time = max(max_time, time.mktime(cache["endtime"].timetuple()))
            plt.gca().add_patch(rectangle, )
            print "x = %i, y = %i, duration = %i" % (time.mktime(cache["starttime"].timetuple()), i*2, cache["duration"])
    
        print jobidmatch
        #plt.axis('scaled')
        plt.xlim([time.mktime(sorted_timeline[0]["starttime"].timetuple()), max_time])
        plt.ylim([0, len(jobidmatch.keys())*2.4])
    
        plt.xlabel("Workflow Time")
        plt.ylabel("Slot on machine")
        plt.title("Duration of downloads on a single host: %s" % host)
    
        red_patch =  mpatches.Patch(color='red', label='UnCached')
        green_patch = mpatches.Patch(color='green', label='Cached')
        plt.legend((red_patch, green_patch), ('UnCached', 'Cached'))
        #plt.legend()
    
    
        plt.savefig("timeline_%s.png" % sorted_timeline[0]["host"])
    



    #for cache_info in results:
    #    if cache_info["initialCached"]:
    #        already_cached.append(cache_info["duration"])
    #    else:
    #        not_cached.append(cache_info["duration"])

    #print "Cached: mean = %lf, median = %lf" % (numpy.mean(already_cached), numpy.median(already_cached))
    #print "Not Cached: mean = %lf, median = %lf" % (numpy.mean(not_cached), numpy.median(not_cached))


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





