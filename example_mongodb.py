import rivr
from rivr.views.mongodb import object_list, object_detail
from os.path import realpath, dirname, join
from rivr.http import ResponseRedirect
from pymongo.objectid import ObjectId

template_dir = join(dirname(realpath(__file__)), 'mongodb')

kwargs = {
    'template_object_name': 'page',
}

@rivr.mongodb
def add_view(request):
    if request.method == 'POST':
        return ResponseRedirect('/%s/' % request.mongodb_collection.save(request.POST))
    return rivr.TemplateResponse(request, 'page_add.html', {})

@rivr.mongodb
def edit_view(request, object_id):
    if request.method == 'POST':
        request.mongodb_collection.update({'_id': ObjectId(object_id)}, request.POST)
        return ResponseRedirect('/%s/' % object_id)
    return object_detail(request, template_name='page_edit.html', **kwargs)

if __name__ == '__main__':
    rivr.serve(rivr.MongoDBMiddleware('localhost', 27017, 'rivr_test', 'pages',
        rivr.TemplateMiddleware(template_dir,
            rivr.Router(
                (r'^$', object_list, kwargs),
                (r'^add/$', add_view),
                (r'^(?P<object_id>[\w\d]+)/edit/$', edit_view),
                (r'^(?P<object_id>[\w\d]+)/$', object_detail, kwargs)
            )
        )
    ))
