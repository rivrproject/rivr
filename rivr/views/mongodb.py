from rivr.template.response import TemplateResponse
from rivr.http import Response, ResponseRedirect, Http404
from rivr.middleware.mongodb import mongodb

try:
    from pymongo.objectid import ObjectId
    import gridfs
except ImportError:
    ObjectId = lambda x: x
    gridfs = None

class GridFSResponse(Response):
    def __init__(self, grid_file):
        super(GridFSResponse, self).__init__(content_type=str(grid_file.content_type))
        self.grid_file = grid_file
    
    def get_content(self):
        return self.grid_file.read()
    
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

#@mongodb
def object_list(request, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = ['%s_list.html' % template_object_name]
        
        if template_object_name == 'object':
            template_name.insert(0, '%s_list.html' % request.mongodb_collection.name)
    
    return TemplateResponse(request, template_name, {
        '%s_list' % template_object_name: request.mongodb_collection.find()
    })
object_list = mongodb(object_list)

#@mongodb
def object_detail(request, lookup, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = ['%s_detail.html' % template_object_name]
        
        if template_object_name == 'object':
            template_name.insert(0, '%s_detail.html' % request.mongodb_collection.name)
    
    return TemplateResponse(request, template_name, {
        template_object_name: request.mongodb_collection.find_one(lookup)
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
        template_object_name: obj
    })

delete_object = object_lookup(delete_object)
delete_object = mongodb(delete_object)
