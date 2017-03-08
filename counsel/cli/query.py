#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Query Consul for a service
   Performs complex consul query providing Node, Service and Checks aggregated information

Usage:
  counsel query [(-h|--help)] (-s service|--service=service)
                              [--limit=number]
                              [--tags=tag1,tag2]
                              [--datacenters=dc1,dc2]
                              [-f filter|--filter=filter [--oneline|--multiline]]
                              [--onlypassing]

Options:
  -s service --service=service      query Consul for the given service [required]
  --limit=number                    limit number result recieved from the query
  --tags=tag1,tag2                  list of tags to filter the query results
  --datacenters=dc1,dc2             list of datacenters to forward queries to
  -f filter --filter=filter         jinja template to format the result
  --oneline                         output results as oneline [requires: --filter]
  --multiline                       output results split into many lines [requires: --filter]
  --onlypassing                     specify to filter query results only with healthy checks
  -h --help                         show this help message and exit

Examples:
  counsel query -s service
  counsel query -s service --tags=tag1,tag2
  counsel query -s service --datacenters=dc2
  counsel query -s service -f '{{ Node.Address }}'

"""
from docopt import docopt
from counsel.helpers import docopt_lstrip, docopt_strtolist


def cli(argv):
    parsed = docopt_lstrip(docopt(__doc__, argv=argv))
    return docopt_strtolist(parsed, 'tags', 'datacenters')
