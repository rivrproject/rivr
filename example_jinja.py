from os.path import realpath, dirname

import rivr
from rivr.jinja import JinjaView, JinjaMiddleware

from jinja2 import Environment, FileSystemLoader
from jinja2.filters import FILTERS

class ExampleView(JinjaView):
    template_name = 'example_template.html'

    def get_context_data(self, **kwargs):
        return {
            'filter_list': FILTERS.keys(),
        }

if __name__ == '__main__':
    rivr.serve(rivr.DebugMiddleware(JinjaMiddleware(Environment(loader=FileSystemLoader(dirname(realpath(__file__)))),
        ExampleView.as_view()
    )))
