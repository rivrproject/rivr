def import_module(name):
    if callable(name):
        return name
    
    if not isinstance(name, str):
        raise ImportError('rivr.import.import_module cannot import %s because it is not a string.' % name)
    
    module = __import__(name)
    for i in name.split('.')[1:]:
        module = getattr(module, i)
    
    return module
