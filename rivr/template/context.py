class Context(object):
    def __init__(self, kwargs={}):
        self.dicts = [kwargs]
    
    def __setitem__(self, key, value):
        self.dicts[-1][key] = value
    
    def __getitem__(self, key):
        for d in reversed(self.dicts):
            if key in d:
                return d[key]
        raise KeyError(key)
    
    def __delitem__(self, key):
        del self.dicts[-1][key]
    
    def __contains__(self, key):
        for d in self.dicts:
            if key in d:
                return True
        return False
    
    def push(self, _dict={}):
        self.dicts.append(_dict)
    
    def pop(self):
        self.dicts.pop()
