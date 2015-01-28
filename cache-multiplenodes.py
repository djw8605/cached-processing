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
    # CacheState = 1;
    cache_re = re.compile(".*CacheState = (\d)\;")
    # HOSTNAME=c1016
    node_re = re.compile(".*HOSTNAME=(.*)$")
    # SLURM_JOBID=231412
    slurm_re = re.compile(".*SLURM_JOBID=(.*)$")


    found_initial = False
    initial_cached = False

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
        cache_match = cache_re.search(line)
        if cache_match and not found_initial:
            found_initial = True
            if cache_match.group(1) != "1":
                initial_cached = True
        node_match = node_re.search(line)
        if node_match:
            hostname = node_match.group(1)
        slurm_match = slurm_re.search(line)
        if slurm_match:
            slurm_jobid = int(slurm_match.group(1))

    # Sat Jan 24 16:02:37 CST 2015
    time_format = "%a %b %d %H:%M:%S %Z %Y"
    start_fmt = datetime.datetime.strptime(start_time, time_format)
    end_fmt = datetime.datetime.strptime(end_time, time_format)

    difference = end_fmt - start_fmt
    seconds = (difference.microseconds + (difference.seconds + difference.days * 24 * 3600) * 10**6) / 10**6
    print "Total seconds = %i" % seconds

    to_return = {"starttime": start_fmt, "endtime": end_fmt, "duration": seconds, "initialCached": initial_cached, "host": hostname, "slurm_jobid": slurm_jobid}

    #return (time.mktime(start_fmt.timetuple()), seconds)
    return to_return
    



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
    print sorted_results

    host = sorted_results[0]["host"]
    collection = []
    i = 0
    plt.axes()

    while host == sorted_results[0]["host"]:
        #rectangle = plt.Rectangle((time.mktime(cache["starttime"].timetuple()), i*2), cache["duration"], 1.5)
        #plt.gca().add_patch(rectangle)
        collection.append(sorted_results[i])
        i+= 1
        host = sorted_results[i]["host"]

    sorted_timeline = sorted(collection, key=lambda cache: cache["starttime"])

    print sorted_timeline
    max_time = 0
    import math
    counter = 0
    jobidmatch = {}

    for i in range(len(sorted_timeline)):
        cache = sorted_results[i]
        if cache["slurm_jobid"] not in jobidmatch:
            jobidmatch[cache["slurm_jobid"]] = counter
            counter+=2
        
        rectangle = plt.Rectangle((time.mktime(cache["starttime"].timetuple()), jobidmatch[cache["slurm_jobid"]]), cache["duration"], 1.5)
        max_time = max(max_time, time.mktime(cache["endtime"].timetuple()))
        plt.gca().add_patch(rectangle)
        print "x = %i, y = %i, duration = %i" % (time.mktime(cache["starttime"].timetuple()), i*2, cache["duration"])

    #plt.axis('scaled')
    plt.xlim([time.mktime(sorted_timeline[0]["starttime"].timetuple()), max_time])
    plt.ylim([0, len(jobidmatch.keys())])

    plt.savefig("timeline.png")




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





