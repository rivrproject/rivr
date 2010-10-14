from rivr.template.response import TemplateResponse
from rivr.middleware.mongodb import mongodb

@mongodb
def object_list(request, template_name=None, template_object_name='object'):
    if not template_name:
        template_name = '%s_list.html' % template_object_name
    
    return TemplateResponse(request, template_name, {
        '%s_list' % template_object_name: request.mongodb_collection.find()
    })

@mongodb
def object_detail(request, template_name=None, object_id=None, slug=None, slug_field='slug', template_object_name='object'):
    if not template_name:
        template_name = '%s_detail.html' % template_object_name
    
    lookup = {}
    
    if object_id:
        from pymongo.objectid import ObjectId
        lookup['_id'] = ObjectId(object_id)
    
    if slug:
        lookup[slug_field] = slug
    
    return TemplateResponse(request, template_name, {
        template_object_name: request.mongodb_collection.find_one(lookup)
    })
