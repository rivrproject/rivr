from rivr import template

register = template.Library()

def escape(value):
    return template.html_escape(value)
register.filter('escape', escape)

def first(value):
    try:
        return value[0]
    except IndexError:
        return ''
register.filter('first', first)

def last(value):
    try:
        return value[-1]
    except IndexError:
        return ''
register.filter('last', last)

def capitalize(value):
    return value.capitalize()
register.filter('capitalize', capitalize)
