
import re
import datetime
import dateutil.parser
import dateutil.tz as dttz
import pytz


def parse_tz(time):

    if "EDT" in time:
        return pytz.timezone("America/Detroit")
    elif "CDT" in time:
        return pytz.timezone("America/Chicago")
    elif "PDT" in time:
        return pytz.timezone("America/Los_Angeles")
    else:
        print "Unknown TZ: %s" % time




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
    # _CONDOR_SLOT=slot1
    slot_re = re.compile(".*_CONDOR_SLOT=(.*)$")
    # ParentCached = "cached-4467@red-foreman.unl.edu"; 
    parent_re = re.compile(".*ParentCached = \"(.*)\"")
    # CacheOriginatorHost = "cached-4467@red-foreman.unl.edu"; 
    origin_re = re.compile(".*CacheOriginatorHost = \"(.*)\"")
    # _condor_BOSCOCluster=dweitzel@crane.unl.edu/pbs
    #cluster_re = re.compile(".*_condor_BOSCOCluster=(.*)$")
    # GLIDEIN_ResourceName=Nebraska
    cluster_re = re.compile(".*GLIDEIN_ResourceName=(.*)$")



    found_initial = False
    initial_cached = False
    slurm_jobid=0

    f = open(filename, 'r')
    for line in f:
        start_match = start_re.search(line)
        if start_match:
            start_time = start_match.group(1)
            #print "started at %s" % start_time
            continue
        end_match = end_re.search(line)
        if end_match:
            end_time = end_match.group(1)
            #print "Ended at %s" % end_time
            continue
        cache_match = cache_re.search(line)
        if cache_match and not found_initial:
            found_initial = True
            if cache_match.group(1) == "3":
                initial_cached = True
            continue
        node_match = node_re.search(line)
        if node_match:
            hostname = node_match.group(1)
            continue
        slurm_match = slurm_re.search(line)
        if slurm_match:
            slurm_jobid = int(slurm_match.group(1))
            continue
        slot_match = slot_re.search(line)
        if slot_match:
            slot_id = slot_match.group(1)
            continue
        parent_match = parent_re.search(line)
        if parent_match:
            parent = parent_match.group(1)
            #print "Parent = " + parent
            continue
        origin_match = origin_re.search(line)
        if origin_match:
            origin = origin_match.group(1)
            #print "Origin = " + origin
            continue
        cluster_match = cluster_re.search(line)
        if cluster_match:
            cluster = cluster_match.group(1)
        #print line

    # Sat Jan 24 16:02:37 CST 2015
    time_format = "%a %b %d %H:%M:%S %Z %Y"
    #print start_time
    #start_fmt = dateutil.parser.parse(start_time, tzinfos=tz_parse)
    start_fmt = dateutil.parser.parse(start_time, ignoretz=True)
    print "string = %s, datetime = %s" % (start_time, str(start_fmt))
    #print start_fmt
    timezone = parse_tz(start_time)
    start_fmt = timezone.localize(start_fmt)

    print start_fmt
    #end_fmt = dateutil.parser.parse(end_time, tzinfos=tz_parse)
    end_fmt = dateutil.parser.parse(end_time, ignoretz=True)
    end_fmt = timezone.localize(end_fmt)
    #if len(start_time.split()[2]) != 2:
    #    start_time = start_time.replace(" %s" % start_time.split()[2], "0%s" % start_time.split()[2], 1)
    #    print "New start_time = %s" % start_time
        
    #start_time = start_time.replace("EDT", "CDT")
    #start_fmt = datetime.datetime.strptime(start_time, time_format)
    #end_fmt = datetime.datetime.strptime(end_time, time_format)

    difference = end_fmt - start_fmt
    seconds = (difference.microseconds + (difference.seconds + difference.days * 24 * 3600) * 10**6) / 10**6
    #print "Total seconds = %i" % seconds

    to_return = {"starttime": start_fmt, "endtime": end_fmt, "duration": seconds, "initialCached": initial_cached, "host": hostname, "slurm_jobid": slurm_jobid, 
            "_CONDOR_SLOT": slot_id, "cluster": cluster}

    #print "Origin = " + origin
    #print "Parent = " + parent
    if initial_cached:
        to_return["mode"] = "cached"
    elif origin == parent:
        to_return["mode"] = "parent"
    else:
        to_return["mode"] = "child"

    #print "Mode = " + to_return["mode"]

    #return (time.mktime(start_fmt.timetuple()), seconds)
    return to_return




