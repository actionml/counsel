#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Counsel helper tool for Consul discovery database.

Usage:
  counsel [--version] [-h|--help] [-q|--quiet] [--verify]
                                  [-s server|--server=server]
                                  [--dc=dc]
                                  [--token=token]
                                  [--consistency=mode]
                                  <command> [<args>...]

Commands:
  query -s service [<options>]
    Query service (performes complex service query)

  health -s service [<options>]
    Query service health

Options:
  -s server --server=server   specify Consul server host to connect [default: http://127.0.0.1:8500]
                              also allows host:port and host specification
  --dc=dc                     default datacenter used for queries (default: is agent's dc)
  --token=uuid                default ACL token used for queries
  --consistency=mode          consitency mode (default|consistent|stale) [default: default]
  --verify                    specifify to verify the SSL certificate for HTTPS requests
                              [default: False]
  -q --quiet                  quiet mode suppresses error output
  -h --help                   show this help message and exit
  --version                   show version and exit
"""
import importlib
import logging

from docopt import docopt
import counsel

from counsel.log import console
from counsel.helpers import docopt_lstrip, dict_compact


COMMANDS = ('query', 'health')
app = counsel.Counsel()


def set_output_format(kwargs):
    if kwargs.pop('oneline', False):
        kwargs['format'] = 'oneline'
    if kwargs.pop('multiline', False):
        kwargs['format'] = 'multiline'

def query_service(**kwargs):
    '''Invoke counsel query_service
    '''
    opts = dict_compact(kwargs, unwanted=('help', 'query'))
    set_output_format(opts)
    app.display_query_service(**opts)

def health_service(**kwargs):
    opts = dict_compact(kwargs, unwanted=('help', 'health'))
    set_output_format(opts)
    app.display_health_service(**opts)


def main():
    parsed = docopt(__doc__, version=counsel.__version__, options_first=True)
    parsed = docopt_lstrip(parsed)

    # sub command and its args
    command = parsed.pop('<command>')
    args = [command] + parsed.pop('<args>')

    # set consul default options
    if parsed.pop('quiet'):
        console.setLevel(logging.FATAL+1)

    parsed = dict_compact(parsed, unwanted=('help', 'version'))
    app.connect_options(**parsed)

    # override agent DC if given
    dc = parsed.get('dc', None)

    # sub-command
    if command in COMMANDS:
        res = importlib.import_module('counsel.cli.{}'.format(command))
        parsed = getattr(res, 'cli')(args)

        if command == 'query':
            query_service(dc=dc, **parsed)

        if command == 'health':
            health_service(dc=dc, **parsed)



if __name__ == '__main__':
    main()
