from urllib.parse import urlparse


def dict_compact(_dict, unwanted=None):
    """Drop dictionary items with None values.
    """
    unwanted = unwanted if unwanted else ()

    return {
        k: v for k, v in _dict.items()
        if v is not None and k not in unwanted
    }


def http_urlparse(url):
    """Parse url and return result.
    """
    if not url.startswith('http'):
        url = '//{}'.format(url)

    return urlparse(url, scheme='http')


def docopt_lstrip(adict):
    '''Strip leading - in docpt options keys
    '''
    return {k.lstrip('-'): v for k, v in adict.items()}


def docopt_strtolist(adict, *args):
    '''Convert the given docopt dictionary values to list
    '''
    return {
        k: v.split(',') if v and k in args
           else v
        for k, v in adict.items()
    }
