from os.path import join

from rivr import template

class TemplateLoadError(Exception):
    def __init__(self, template, tried):
        self.template = template
        self.tried = tried
    
    def __str__(self):
        return 'Unable to load %s' % self.template

class Loader(object):
    def __init__(self):
        self.template_dirs = []
    
    def load_template(self, template_names):
        tried = []
        
        if isinstance(template_names, str):
            template_names = [template_names]
        
        for template_name in template_names:
            for template_dir in self.template_dirs:
                filepath = join(template_dir, template_name)
                try:
                    f = open(filepath)
                    try:
                        return f.read()
                    finally:
                        f.close()
                except IOError:
                    tried.append(filepath)
            
        return tried
    
    def get_template(self, template_name):
        template_content = self.load_template(template_name)
        
        if isinstance(template_content, list):
            raise TemplateLoadError(template_name, template_content)
        
        return template.Template(template_content)
