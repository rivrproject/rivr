import math

from rivr.template.response import TemplateResponse
from rivr.http import Response, ResponseRedirect, Http404
from rivr.middleware.mongodb import mongodb

try:
    from pymongo.objectid import ObjectId
    from pymongo import json_util
    import gridfs
except ImportError:
    ObjectId = lambda x: x
    gridfs = None

class GridFSResponse(Response):
    def __init__(self, grid_file):
        super(GridFSResponse, self).__init__(content_type=str(grid_file.content_type))
        self.grid_file = grid_file
    
    def get_content(self):
        if not hasattr(self, '_content'):
            self._content = self.grid_file.read()
        return self._content
    
    def set_content(self, value):
        pass
    content = property(get_content, set_content)

#@mongodb
def gridfs_view(request, object_id):
    f = request.mongodb_gridfs.get(ObjectId(object_id))
    return GridFSResponse(f)
gridfs_view = mongodb(gridfs_view, collection=False, gridfs=True)

def object_lookup(func):
    def new_func(request, object_id=None, slug=None, slug_field='slug', *args, **kwargs):
        lookup = {}
        
        if object_id:
            lookup['_id'] = ObjectId(object_id)
        
        if slug:
            lookup[slug_field] = slug
        
        return func(request, lookup, *args, **kwargs)
    return new_func

lookup_filters = {
    'int': int,
    'gt': lambda x: {'$gt': int(x)},
    'gte': lambda x: {'$gte': int(x)},
    'lt': lambda x: {'$lt': int(x)},
    'lte': lambda x: {'$lte': int(x)},
    'regex': lambda x: {'$regex': x},
    'iregex': lambda x: {'$regex': x, '$options': 'i'},
}

#@mongodb
def object_list(request, page=1, paginate_by=20, template_name=None, template_object_name='object', serializable=False):
    if not template_name:
        template_name = ['%s_list.html' % template_object_name]
        
        if template_object_name == 'object':
            template_name.insert(0, '%s_list.html' % request.mongodb_collection.name)
    
    lookup = {}
    output = 'template'
    
    for l in request.GET:
        if l == 'page':
            page = request.GET[l]
        elif l == 'o':
            output = request.GET[l]
        elif '__' in l:
            try:
                key, f = l.split('__')
                lookup[key] = lookup_filters[f](request.GET[l])
            except:
                continue
        else:
            lookup[l] = request.GET[l]
    
    try:
        page = int(page)
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        page = 1
    
    query = request.mongodb_collection.find(lookup)
    paged_query = query.skip(paginate_by * (page - 1)).limit(paginate_by)
    
    if output == 'json' and serializable:
        import json
        serialized = json.dumps([x for x in paged_query], default=json_util.default)
        return Response(serialized, content_type='application/json')
    
    return TemplateResponse(request, template_name, {
        '%s_list' % template_object_name: paged_query,
        'mongodb_collection': request.mongodb_collection.name,
        # Pagination
        'page': page,
        'paginate_by': paginate_by,
        'page_count': int(math.ceil(float(query.count()) / float(paginate_by)))
    })
object_list = mongodb(object_list)

#@mongodb
def object_detail(request, lookup, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = ['%s_detail.html' % template_object_name]
        
        if template_object_name == 'object':
            template_name.insert(0, '%s_detail.html' % request.mongodb_collection.name)
    
    return TemplateResponse(request, template_name, {
        template_object_name: request.mongodb_collection.find_one(lookup),
        'mongodb_collection': request.mongodb_collection.name
    })

object_detail = object_lookup(object_detail)
object_detail = mongodb(object_detail)

#@mongodb
def delete_object(request, lookup, template_name=None, template_object_name='object', post_delete_redirect='/'):
    obj = request.mongodb_collection.find_one(lookup)
    
    if not obj:
        raise Http404
    
    if request.method == 'POST':
        request.mongodb_collection.remove(lookup)
        return ResponseRedirect(post_delete_redirect)
    
    if not template_name:
        template_name = ['%s_confirm_delete.html' % template_object_name]
        
        if template_object_name == 'object':
            template_name.insert(0, '%s_confirm_delete.html' % request.mongodb_collection.name)
    
    return TemplateResponse(request, template_name, {
        template_object_name: obj,
        'mongodb_collection': request.mongodb_collection.name
    })

delete_object = object_lookup(delete_object)
delete_object = mongodb(delete_object)
