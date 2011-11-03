import math

from rivr.http import Response, ResponseRedirect
from rivr.views.base import View, TemplateView

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


class GridFSView(View):
    def get_gridfs(self):
        return gridfs.GridFS(self.request.mongodb_database)

    def get_file(self):
        object_id = self.kwargs.get('object_id', None)
        return self.get_gridfs().get(ObjectId(object_id))

    def get(self, request, *args, **kwargs):
        return GridFSResponse(self.get_file())

class MongoMixin(object):
    collection = None

    def get_collection_name(self):
        if "mongodb_collection" in self.kwargs:
            return self.kwargs['mongodb_collection']

        if self.collection:
            return self.collection

        raise Exception("MongoMixin requires either a definition of 'collection'"
                        "or a implementation of 'get_collection_name()'")

    def get_collection(self):
        return self.request.mongodb_database[self.get_collection_name()]

class SingleObjectMixin(MongoMixin):
    slug_field = 'slug'
    context_object_name = None

    def get_lookup(self):
        lookup = {}
        object_id = self.kwargs.get('object_id', None)
        slug = self.kwargs.get('slug', None)

        if object_id:
            lookup['_id'] = ObjectId(object_id)
        elif slug:
            lookup[self.get_slug_field()] = slug
        else:
            raise AttributeError("%s must be called with either an object_id"
                                 "or a slug" % self.__class__.__name__)

        return lookup

    def get_object(self):
        return self.get_collection().find_one(self.get_lookup())

    def get_slug_field(self):
        return self.slug_field
 
    def get_context_object_name(self, obj):
        if self.context_object_name:
            return self.context_object_name
        return 'object'

    def get_context_data(self, **kwargs):
        context = kwargs
        obj = self.get_object()
        context_object_name = self.get_context_object_name(obj)
        if context_object_name:
            context[context_object_name] = obj
        context['mongodb_collection'] = self.get_collection_name()
        return context

    def get_template_names(self):
        try:
            names = super(SingleObjectMixin, self).get_template_names()
        except:
            names = '%s_detail.html' % self.get_context_object_name(None)

        return names


class DetailView(SingleObjectMixin, TemplateView):
    pass

class MultipleObjectMixin(MongoMixin):
    context_object_name = None
    paginate_by = 20
    allow_filters = True

    lookup_filters = {
        'int': int,
        'gt': lambda x: {'$gt': int(x)},
        'gte': lambda x: {'$gte': int(x)},
        'lt': lambda x: {'$lt': int(x)},
        'lte': lambda x: {'$lte': int(x)},
        'regex': lambda x: {'$regex': x},
        'iregex': lambda x: {'$regex': x, '$options': 'i'},
        'id': lambda x: {'_id': ObjectId(x)},
    }

    def get_lookup(self):
        lookup = {}

        if self.allow_filters:
            for l in self.request.GET:
                if l == 'page':
                    continue
                elif '__' in l:
                    key, f = l.split('__')
                    if f in self.lookup_filters:
                        try:
                            lookup[key] = self.lookup_filters[f](self.request.GET[l])
                        except:
                            pass
                else:
                    lookup[l] = self.request.GET[l]

        return lookup

    def resolve_page(self):
        self.page = 1

        try:
            self.page = int(self.request.GET['page'])
        except (KeyError, TypeError, ValueError):
            pass

        if 'page' in self.kwargs:
            try:
                self.page = int(self.kwargs['page'])
            except:
                pass

        if self.page < 1:
            self.page = 1

    def get_object_list(self):
        self.resolve_page()

        query = self.get_collection().find(self.get_lookup())
        paged_query = query.skip(self.paginate_by * (self.page - 1)).limit(self.paginate_by)
        self.page_count = int(math.ceil(float(query.count()) / float(self.paginate_by)))
        return paged_query

    def get_context_object_name(self, object_list):
        if self.context_object_name:
            return self.context_object_name
        return 'object'

    def get_context_data(self, **kwargs):
        context = kwargs
        object_list = self.get_object_list()
        context_object_name = self.get_context_object_name(object_list)
        if context_object_name:
            context['%s_list' % context_object_name] = object_list

        context['paginate_by'] = self.paginate_by
        context['page'] = self.page
        context['page_count'] = self.page_count

        context['mongodb_collection'] = self.get_collection_name()

        return context

    def get_template_names(self):
        try:
            names = super(MultipleObjectMixin, self).get_template_names()
        except:
            names = '%s_list.html' % self.get_context_object_name(None)

        return names


class ListView(MultipleObjectMixin, TemplateView):
    pass

class DeleteView(DetailView):
    post_delete_redirect = '/'

    def post(self, request, *args, **kwargs):
        self.get_collection().remove(self.get_object())
        return ResponseRedirect(self.post_delete_redirect)

    def get_template_names(self):
        if self.template_name:
            return self.template_name
        return '%s_confirm_delete.html' % self.get_context_object_name(None)

