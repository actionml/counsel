#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Query Consul service health

Usage:
  counsel health [(-h|--help)] (-s service|--service=service)
                               [-t tag|--tag=tag]
                               [-f filter|--filter=filter [--oneline|--multiline]]
                               [--onlypassing]

Options:
  -s service --service=service      query Consul for the given service [required]
  -t tag --tags=tag                 tag to filter query results
  -f filter --filter=filter         jinja template to format the result
  --oneline                         output results as oneline [requires: --filter]
  --multiline                       output results split into many lines [requires: --filter]
  --onlypassing                     specify to filter query results only with healthy checks
  -h --help                         show this help message and exit

Examples:
  counsel health -s service
  counsel health -s service --tag=eu-central-1
  counsel health -s service -f '{{ Node.Address }}'

"""
from docopt import docopt
from counsel.helpers import docopt_lstrip


def cli(argv):
    parsed = docopt_lstrip(docopt(__doc__, argv=argv))
    return parsed
