import json
import jinja2
import inspect

import counsel.jinja_filters

from counsel.log import log


class Render(object):
    '''Base Render class is used to transform data into another form.
       For instance it's used as the base for JinjaRender which generates
       a string (or a list of strings) from the Jinja template.

    '''
    class Error(Exception): pass
    class NoRenderMethod(Exception): pass

    def __init__(self, render_method=None):
        self.render_method = render_method
        self.result = None

    def render(self, data, **kwargs):
        '''Invokes _render method for the data recursively (in case it's a list)
        '''

        if isinstance(data, list):
            combined = []
            for context in data:
                rendered = self._render(context, **kwargs)
                if rendered:
                    combined.append(rendered)
            return combined

        elif isinstance(data, dict):
            return self._render(data, **kwargs)
        else:
            raise Render.Error("Expects dict or list, %s provided" %
                               type(self))

    def _render(self, data, **kwargs):
        '''Invokes render_method
        '''
        if not self.render_method or not callable(self.render_method):
            raise Render.NoRenderMethod('render_method has to be a function')

        try:
            return self.render_method(data, **kwargs)
        except Exception as e:
            log.error('render failed: %s', e)


class JinjaRender(Render):
    '''Renders template for an object or a collection of objects.
       Each object is used as the Jinja context.
    '''

    def __init__(self, template):
        self.template = template

        render_method = JinjaRender.get_render_method(template)
        super(self.__class__, self).__init__(render_method)

    @staticmethod
    def get_render_method(template):
        '''Make template with custom filters preloaded
        '''
        try:
            render_method = None
            jinja = jinja2.Environment()
            filter_functions = inspect.getmembers(counsel.jinja_filters,
                                                  inspect.isfunction)
            for func_name, func in filter_functions:
                jinja.filters[func_name] = func

            render_method = jinja.from_string(template).render

        except jinja2.exceptions.TemplateSyntaxError as e:
            log.error('jinja2 syntax error: %s', e)

        return render_method


class Formatter(object):

    class Base(object):
        @staticmethod
        def json(data, sort_keys=True, **kwargs):
            return json.dumps(data, sort_keys=sort_keys, **kwargs)

    class JSON(Base):
        def output(self, data):
            return self.json(data, indent=4)

    class Oneline(Base):
        def output(self, data):
            if isinstance(data, list):
                return ' '.join(data)
            else:
                return self.json(data)

    class Multiline(Base):
        def output(self, data):
            if isinstance(data, list):
                res = "\n".join(data)
                return res
            else:
                return self.json(data)

    FACTORY = {
        'json': JSON,
        'oneline': Oneline,
        'multiline': Multiline
    }

    def __init__(self, output_format):
        self.formatter = self.FACTORY[output_format]()

    def output(self, data):
        if data:
            print(self.formatter.output(data))
