import unittest

from rivr.template import Template, Context, html_escape


class TemplateTest(unittest.TestCase):
    def test_context(self):
        c = Context()
        c.push({'primary': 'white', 'secondary': 'red'})
        c.push({'secondary': 'blue'})
        c.push({'extra': 5})
        self.assertEqual(c['extra'], 5)
        c.pop()
        self.assertFalse('extra' in c)
        self.assertEqual(c['primary'], 'white')
        self.assertEqual(c['secondary'], 'blue')
        c.pop()
        self.assertEqual(c['secondary'], 'red')

    def test_template_variable(self):
        c = Context({
            'target': 'world',
            'dict': {'letter': 'c'},
            'array': ['one', 'two'],
        })

        t = Template('Hello {{ target }}')
        self.assertEqual(t.render(c), 'Hello world')

        t = Template('{{ dict.letter }}')
        self.assertEqual(t.render(c), 'c')

        t = Template('{{ array.1 }}')
        self.assertEqual(t.render(c), 'two')

    def test_template_filter(self):
        c = Context({'target': 'world'})
        t = Template('Hello {{ target|capitalize }}')
        self.assertEqual(t.render(c), 'Hello World')

    def test_escape(self):
        self.assertEqual(html_escape('<html>'), '&lt;html&gt;')

