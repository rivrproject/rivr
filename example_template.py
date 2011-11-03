from os import path

import rivr
from rivr.template.defaulttags import register as tag_lib
from rivr.template.defaultfilters import register as filter_lib
from rivr.template.loader_tags import register as loader_lib

template_dir = path.join(path.dirname(path.realpath(__file__)), 'example_templates')

class TemplateTagView(rivr.views.TemplateView):
    template_name = 'example_template.html'

    def get_context_data(self, **kwargs):
        return {
            'tag_list': tag_lib.tags,
            'filter_list': filter_lib.filters,
            'loader_list': loader_lib.tags,
            'params': kwargs,
        }

if __name__ == '__main__':
    view = TemplateTagView.as_view()

    app = rivr.MiddlewareController(view,
        rivr.TemplateMiddleware(template_dirs=template_dir)        
    )

    rivr.serve(app)

