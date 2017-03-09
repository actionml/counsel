import sys
import json
import hashlib
from collections import namedtuple

import consul
import counsel.results as results
import requests.exceptions
from counsel.log import log
from counsel.helpers import http_urlparse, dict_compact


class Agent(object):
    agent = consul.Consul()


class ConsulAPI(object):
    @property
    def agent(self):
        return Agent.agent

    @agent.setter
    def agent(self, value):
        Agent.agent = value

    class Call(object):
        def __init__(self, api_chain=None):
            self.api = api_chain or Agent.agent

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def __call__(self, *args, **kwargs):
            '''Invoke api method
            '''
            try:
                return self.api(*args, **dict_compact(kwargs))

            except requests.exceptions.RequestException as e: 
                log.error('%s', e)
                sys.exit(1)

            except consul.base.ConsulException as e:
                log.error("%s\n\t==> %s\n", e,
                          self.__class__.params_detail(dict_compact(kwargs))
                         )
                sys.exit(1)

        def __getattr__(self, method_name):
            '''Forward requests to API.
               Creates reqursive chain of ApiCall instances.
            '''
            try:
                chain_method = getattr(self.api, method_name)
                return ConsulAPI.Call(chain_method)
            except AttributeError as e:
                log.error('Cannot invoke api method: %s', e)
                sys.exit(1)

        @staticmethod
        def params_detail(kwargs):
            return ', '.join(["{}={}".format(k, v) for k, v in kwargs.items()])


class Counsel(ConsulAPI):
    """Counsel App
    """

    def connect_options(
            self, 
            server='http://127.0.0.1:8500',
            dc=None,
            token=None,
            consistency='default',
            verify=True):
        """
            Initializes consul api with the specified options.
            Some of the options including host, port have their defaults.
        """
        url = http_urlparse(server)
        self.agent = consul.Consul(
            host=url.hostname,
            port=url.port,
            dc=dc,
            token=token,
            scheme=url.scheme,
            consistency=consistency,
            verify=verify)

    def __init__(self):
        super(Counsel, self).__init__()

    @staticmethod
    def jinja_filter(template, collection):
        '''Applies Jinja filtering to the given collection
           (which is technically list of contexts)
        '''
        rendered_collection = results.JinjaRender(template)
        rendered_collection.render(collection, iterate=True)
        return rendered_collection.result

    def display_query_service(
            self, service, limit=None, tags=None,
            dc=None, datacenters=None, onlypassing=None,
            filter=None, format='json'):
        '''Displays query service
        '''
        rendered_collection = None
        res = self.query_service(service, limit=limit, tags=tags, 
                                 dc=dc, datacenters=datacenters,
                                 onlypassing=onlypassing)

        # Filter query list, result contextes are stored in res['Nodes']
        if filter:
            rendered_collection = self.jinja_filter(template=filter,
                                                    collection=res['Nodes'])

        formatter = results.Formatter(output_format=format)
        formatter.output(rendered_collection or res)
        return True


    def display_health_service(
            self, service, filter=None, format='json',
            tag=None, dc=None, onlypassing=None):
        '''Displays health service query
        '''
        rendered_collection = None
        res = self.health_service(service,
                                  tag=tag,
                                  dc=dc,
                                  onlypassing=onlypassing)
        if filter:
            rendered_collection = self.jinja_filter(template=filter, collection=res)

        formatter = results.Formatter(output_format=format)
        formatter.output(rendered_collection or res)
        return True


    @staticmethod
    def query_service(service, tags=None, dc=None,
                      datacenters=None, onlypassing=None, limit=None):
        '''Invoke query service api calls
        '''

        query = Counsel.Query()
        query.options(service,
                      tags=tags,
                      datacenters=datacenters,
                      onlypassing=onlypassing)

        # create, execute and cleanup the query
        result = query.execute(dc=dc, limit=limit)
        query.cleanup()

        return result

    @staticmethod
    def health_service(service, onlypassing=None, tag=None, dc=None):
        '''Invoke health service api call
        '''
        health = Counsel.Health()
        result = health.service(service,
                                onlypassing=onlypassing,
                                tag=tag,
                                dc=dc)
        return result


    class Query(ConsulAPI):
        '''Creates prepared service query
        '''

        class CachedQuery(namedtuple('CachedQuery', 'uniqname id')):
            pass

        def __init__(self):
            super(self.__class__, self).__init__()
            # self.service_match = "${match(0)}"
            self._options = {}
            self.query_cache = {}

        def execute(self, token=None, dc=None, near=None, limit=None):
            ''' Perform prepared service query

                /v1/query/<query or name>/execute
            '''
            result = None

            # Prepared queries can be executed only up by name!

            with ConsulAPI.Call() as api:
                result = api.query.execute(
                    self.query.uniqname,
                    token=token,
                    dc=dc,
                    near=near,
                    limit=limit)

            return result

        def options(self, service_or_match,
                    tags=None,
                    datacenters=None,
                    onlypassing=None):
            ''' Set query meaningful options which are further hashed and 
                used as an unique query_id.
            '''
            self._options = {
                # BUG: Passing match expression didn't work, so regexp is useless (v0.7.5)!
                'service': service_or_match,
                'regexp': None,
                'datacenters': datacenters,
                'onlypassing': onlypassing,
                'tags': tags
            }

        @property
        def query(self):
            '''Retrieves query from in-mem cache if it exists otherwise
               create consul "prepared" query and cache it.
            '''
            uniqname = self.uniqname

            if uniqname not in self.query_cache.keys():
                with ConsulAPI.Call() as api:
                    cached_query = None

                    # Query might exist in consul but not in the local cache
                    for _query in api.query.list():
                        if _query['Name'] == uniqname:
                            cached_query = self.CachedQuery(
                                uniqname=uniqname, id=_query['ID'])

                    # Create query
                    if not cached_query:
                        query_id = api.query.create(name=uniqname,
                                                    **self._options)['ID']

                        cached_query = self.CachedQuery(
                            uniqname=uniqname, id=query_id)

                    self.query_cache[uniqname] = cached_query

            return cached_query

        @property
        def uniqname(self):
            if not self._options:
                raise RuntimeError('Cannot load or initialize an empty query.')

            serialized = json.dumps(self._options, sort_keys=True).encode('utf-8')
            sha256 = hashlib.sha256(serialized).hexdigest()
            return 'counsel-{}'.format(sha256)

        def cleanup(self):
            ''' Trim Counsel prepared queries
            '''
            for query in list(self.query_cache.values()):
                with ConsulAPI.Call() as api:
                    api.query.delete(query.id)
                    self.query_cache.pop(query.uniqname)

            return True


    class Health(ConsulAPI):
        '''Creates service health query

           Interface:
               service(service, index=None, wait=None, passing=None,
               tag=None, dc=None, near=None, token=None)
        '''

        def __init__(self):
            super(self.__class__, self).__init__()

        @staticmethod
        def service(service, onlypassing=None, tag=None, dc=None, near=None, token=None):
            '''Query service health

               /v1/health/service/<service>
            '''
            result = None

            # Prepared query templates can only be resolved up by name
            # (during execution only)
            with ConsulAPI.Call() as api:
                _, result = api.health.service(
                    service,
                    passing=onlypassing,
                    tag=tag,
                    dc=dc,
                    near=near,
                    token=token)

            return result
