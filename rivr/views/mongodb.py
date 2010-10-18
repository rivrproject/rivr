from rivr.template.response import TemplateResponse
from rivr.http import ResponseRedirect, Http404
from rivr.middleware.mongodb import mongodb

def object_lookup(func):
    def new_func(request, object_id=None, slug=None, slug_field='slug', *args, **kwargs):
        lookup = {}
        
        if object_id:
            from pymongo.objectid import ObjectId
            lookup['_id'] = ObjectId(object_id)
        
        if slug:
            lookup[slug_field] = slug
        
        return func(request, lookup, *args, **kwargs)
    return new_func

@mongodb
def object_list(request, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = '%s_list.html' % template_object_name
    
    return TemplateResponse(request, template_name, {
        '%s_list' % template_object_name: request.mongodb_collection.find()
    })

def object_detail(request, lookup, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = '%s_detail.html' % template_object_name
    
    return TemplateResponse(request, template_name, {
        template_object_name: request.mongodb_collection.find_one(lookup)
    })

object_detail = object_lookup(object_detail)
object_detail = mongodb(object_detail)

def delete_object(request, lookup, template_name=None, template_object_name='object', post_delete_redirect='/'):
    obj = request.mongodb_collection.find_one(lookup)
    
    if not obj:
        raise Http404
    
    if request.method == 'POST':
        request.mongodb_collection.remove(lookup)
        return ResponseRedirect(post_delete_redirect)
    
    if not template_name:
        template_name = '%s_confirm_delete.html' % template_object_name
    
    return TemplateResponse(request, template_name, {
        template_object_name: obj
    })

delete_object = object_lookup(delete_object)
delete_object = mongodb(delete_object)
