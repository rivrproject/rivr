from rivr import template

register = template.Library()

def escape(value):
    return template.html_escape(value)
register.filter('escape', escape)
