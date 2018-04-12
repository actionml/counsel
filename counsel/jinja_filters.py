import json

class Dict(dict):
    pass
    # def __str__(self):
    #     super(type).__str__()
    #     # return json.dumps(self)

def split(string, sep, maxsplit=1):
    return string.split(sep, maxsplit)


def todict(iterator):
    '''Returns a dict with overrided __str__
    '''
    return Dict({k: v for k, v in iterator})
