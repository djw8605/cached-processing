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
from dateutil import tz
import pytz

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


def unix_time(dt):
    #print dt
    dt = dt.astimezone(tz.tzlocal())
    #print "new dt = %s" % str(dt)
    epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = epoch.replace(tzinfo = tz.tzlocal())
    #print epoch
    delta = dt - epoch
    return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6


def main():
    parser = optparse.OptionParser()
    add_options(parser)

    (options, args) = parser.parse_args()
    
    filesize = int(args.pop(0))

    pool = Pool(processes = options.processes)
    results = pool.map(parse_file, args)

    timings = {}

    for result in results:
        start_time = unix_time(result['starttime'])
        end_time = unix_time(result['endtime'])
        print "Start time = %i, end time = %i" % (start_time, end_time)

        # Calculate the transfer speed
        transfer_speed = (float(filesize) / float(end_time - start_time)) / (1024**2)
        print "Transfer Time = %lf, transfer speed = %lf" % (float(end_time - start_time), transfer_speed)

        # Add the start time
        if start_time not in timings:
            timings[start_time] = 0

        timings[start_time] += transfer_speed

        # Add the end time
        if end_time not in timings:
            timings[end_time] = 0

        timings[end_time] -= transfer_speed

    

    import operator
    sorted_times = sorted(timings.items(), key=operator.itemgetter(0))

    # loop through the graph with a running total
    running_total = 0.0
    timeline = []
    for sorted_entry in sorted_times:
        running_total = sorted_entry[1] + running_total
        timeline.append((sorted_entry[0], running_total))



    print timeline
    #print zip(*timeline)

    split = zip(*timeline)
    x = split[0]
    y = split[1]
    print x
    print y
    plt.plot(x, y, label="Effective Bandwidth")
    plt.plot([numpy.amin(x), numpy.amax(x)], [1024/8, 1024/8], label="Origin's Available Bandwidth")
    plt.axis([numpy.amin(x), numpy.amax(x), 0, 2000])
    plt.xlabel("Time")
    plt.legend()
    plt.ylabel("MB/s")
    plt.title("Effective Bandwidth for Bittorrent Transfers")
    plt.savefig("transfer_speed.png")


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





