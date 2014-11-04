

import optparse
import os
import re

# From: https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def parse_file(logfile, graph):
  
  if not os.path.exists(logfile):
    print "Logfile %s doesn't exist" % logfile
    return
    
  print "Examing file %s" % logfile
    
  # Now, start parsing the file
  # Example:
  # Got block of size 16384 bytes from [::ffff:10.137.11.4]:6884, peer_id = -LT1000-ktC_fZfzZadv
  block_finish_re = re.compile(".*Got block of size (\d+) bytes from (.*), peer_id = (.*)$")
  block_finish_fallthrough = re.compile(".*Got block of size (\d+) bytes from.*, peer_id = .*$")
  
  # DaemonCore: command socket at <10.138.14.1:55477?noUDP>
  dest_address = re.compile(".*DaemonCore: command socket at \<([\d\.]+)\:.*>")
  # Started libtorrent on port: 6882
  dest_port = re.compile(".*Started libtorrent on port: ([\d]+)")
  
  my_address = ""
  
  f = open(logfile, 'r')
  for line in f:
    
    
    block_match = block_finish_re.search(line)
    if block_match:
      block_size = block_match.group(1)
      source_address = block_match.group(2)
      peer_id = block_match.group(3)
      
      if source_address.startswith("127.0.0.1"):
        source_address = source_address.replace("127.0.0.1", my_ip)
      elif source_address.startswith("[::1]"):
        source_address = source_address.replace("[::1]", my_ip)
      elif source_address.startswith("[::ffff:"):
        source_address = source_address.replace("[::ffff:", "")
        source_address = source_address.replace("]", "")
      
      if peer_id not in my_graph:
        my_graph[peer_id] = 0
      my_graph[peer_id] += int(block_size)
      continue
      
    dest_address_match = dest_address.search(line)
    if dest_address_match:
      my_address = dest_address_match.group(1)
      my_ip = my_address
      continue
      
    dest_port_match = dest_port.search(line)
    if dest_port_match:
      my_address = "%s:%s" % (my_address, dest_port_match.group(1))
      print "I'm listening on address %s" % my_address
      if my_address not in graph:
        graph[my_address] = {}
        
      my_graph = graph[my_address]
      continue
      
    block_finish_fallthrough_match = block_finish_fallthrough.search(line)
    if block_finish_fallthrough_match:
      print "Block finish didn't catch: %s" % line
      continue
      
  keys = my_graph.keys()
  keys.sort()
  print keys
    
  
def output_dot(output_file, graph):
  
  output_f = open(output_file, 'w')
  
  output_f.write("digraph {\n")
  
  for dest in graph:
    for source in graph[dest]:
      output_f.write("\"%s\" -> \"%s\"[label=\"%s\",weight=\"%i\"];\n" %\
      (source, dest, sizeof_fmt(graph[dest][source]), int(graph[dest][source]/1000)))
  
  output_f.write("}\n")
  


def add_options(parser):
  pass


def main():
  parser = optparse.OptionParser()
  add_options(parser)
  
  (options, args) = parser.parse_args()
  
  output_file = args[0]
  args.pop(0)
  
  graph = {}
  
  for file in args:
    parse_file(file, graph)

  output_dot(output_file, graph)
  print graph


if __name__ == "__main__":
  main()
