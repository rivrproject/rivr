from os.path import realpath, dirname
import rivr
from rivr.template.defaulttags import register as tag_lib
from rivr.template.defaultfilters import register as filter_lib

template_dir = dirname(realpath(__file__))

def view(request):
    return rivr.TemplateResponse(request, 'example_template.html', {
        'tag_list': tag_lib.tags,
        'filter_list': filter_lib.filters,
    })

if __name__ == '__main__':
    rivr.serve(rivr.TemplateMiddleware(template_dir, rivr.Router(
        (r'^$', rivr.direct_to_template, {
            'template': 'example_template.html',
            'extra_context': {
                'tag_list': tag_lib.tags,
                'filter_list': filter_lib.filters,
            }}),
        (r'^view/$', view)
    )))
