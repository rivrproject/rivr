from os.path import realpath, dirname, join


import rivr
from rivr.views.base import TemplateView
from rivr.views.mongodb import MongoMixin, DetailView, ListView, DeleteView
from rivr.http import ResponseRedirect
from rivr.middleware.mongodb import MongoMiddleware

template_dir = join(dirname(realpath(__file__)), 'mongodb')

class AddView(MongoMixin, TemplateView):
    template_name = 'page_add.html'
    collection = 'pages'

    def post(self, request, *args, **kwargs):
        return ResponseRedirect('/%s/' % self.get_collection().save(request.POST))

class EditView(DetailView):
    def post(self, request, *args, **kwargs):
        self.get_collection().update(self.get_object(), request.POST)
        return ResponseRedirect('/%s/' % object_id)

if __name__ == '__main__':
    rivr.serve(
        MongoMiddleware(
            rivr.TemplateMiddleware(template_dir,
            rivr.Router(
                (r'^$', ListView.as_view(collection='pages', context_object_name='page')),
                (r'^add/$', AddView.as_view()),
                (r'^(?P<object_id>[\w\d]+)/edit/$', EditView.as_view(collection='pages', context_object_name='page')),
                (r'^(?P<object_id>[\w\d]+)/delete/$', DeleteView.as_view(collection='pages', context_object_name='page')),
                (r'^(?P<object_id>[\w\d]+)/$', DetailView.as_view(collection='pages', context_object_name='page'))
            )
        ), "mongodb://localhost/rivr")
    )
