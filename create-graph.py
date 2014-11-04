

import optparse
import os
import re
from multiprocessing import Pool

map_peerid_ipaddr = {}

# From: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def parse_file(logfile):
  
  if not os.path.exists(logfile):
    print "Logfile %s doesn't exist" % logfile
    return
    
  print "Examining file %s" % logfile
  
  graph = {}
    
  # Now, start parsing the file
  # Example:
  # Got block of size 16384 bytes from [::ffff:10.137.11.4]:6884, peer_id = -LT1000-ktC_fZfzZadv
  block_finish_re = re.compile(".*Got block of size (\d+) bytes from (.*), peer_id = (.*)$")
  block_finish_fallthrough = re.compile(".*Got block of size (\d+) bytes from.*")
  
  # DaemonCore: command socket at <10.138.14.1:55477?noUDP>
  dest_address = re.compile(".*DaemonCore: command socket at \<([\d\.]+)\:.*>")
  # Started libtorrent on port: 6882
  dest_port = re.compile(".*Started libtorrent on port: ([\d]+)")
  
  # Peer Id: -LT1000-jwjcn9t(Wxgb
  my_peer_id_re = re.compile("Peer Id: (.*)$")
  
  my_peer_id = ""
  
  f = open(logfile, 'r')
  for line in f:
    
    
    block_match = block_finish_re.search(line)
    if block_match:
      block_size = block_match.group(1)
      source_address = block_match.group(2)
      peer_id = block_match.group(3)
      
      if peer_id not in my_graph:
        my_graph[peer_id] = 0
      my_graph[peer_id] += int(block_size)
      
      if peer_id not in map_peerid_ipaddr:
        map_peerid_ipaddr[peer_id] = {}
      
      if source_address not in map_peerid_ipaddr[peer_id]:
        map_peerid_ipaddr[peer_id][source_address] = 0
        
      continue
      
      
    my_peer_id_re_match = my_peer_id_re.search(line)
    if my_peer_id_re_match:
      my_peer_id = my_peer_id_re_match.group(1)
      if my_peer_id not in graph:
        graph[my_peer_id] = {}
      my_graph = graph[my_peer_id]
      continue
      
    block_finish_fallthrough_match = block_finish_fallthrough.search(line)
    if block_finish_fallthrough_match:
      print "Block finish didn't catch: %s" % line
      continue
      
  return graph
  
  
def output_dot(output_file, graph):
  
  output_f = open(output_file, 'w')
  
  output_f.write("digraph {\n")
  
  for dest in graph:
    for source in graph[dest]:
      output_f.write("\"%s\" -> \"%s\"[label=\"%s\",weight=\"%i\"];\n" %\
      (source, dest, sizeof_fmt(graph[dest][source]), int(graph[dest][source]/1000)))
  
  output_f.write("}\n")
  

def output_stats(graph):
  
  for peer_id in map_peerid_ipaddr:
    print "%s: " % peer_id,
    for ipaddr in map_peerid_ipaddr[peer_id]:
      print "%s" % ipaddr, 
    print ""
    

def add_options(parser):
  pass


def main():
  parser = optparse.OptionParser()
  add_options(parser)
  
  (options, args) = parser.parse_args()
  
  output_file = args[0]
  args.pop(0)
  
  graph = {}
  
  pool = Pool(processes = 2)
  results = pool.map(parse_file, args)
  
  print results
  
  #for file in args:
  #  parse_file(file, graph)

  output_dot(output_file, graph)
  print graph


if __name__ == "__main__":
  main()
