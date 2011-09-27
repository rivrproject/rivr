from os.path import realpath, dirname
import rivr
from rivr.template.defaulttags import register as tag_lib
from rivr.template.defaultfilters import register as filter_lib

template_dir = dirname(realpath(__file__))

class TemplateTagView(rivr.TemplateView):
    template_name = 'example_template.html'

    def get_context_data(self, **kwargs):
        return {
            'tag_list': tag_lib.tags,
            'filter_list': filter_lib.filters,
        }

if __name__ == '__main__':
    rivr.serve(rivr.TemplateMiddleware(template_dir, 
        TemplateTagView.as_view()
    ))
