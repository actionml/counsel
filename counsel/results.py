import json
import jinja2

from counsel.log import log


class Render(object):
    '''Base Render class.
       Transforms the given input (context) by calling render method.
    '''
    class NoRenderMethod(Exception):
        pass

    class RenderMethod(object):
        def __init__(self, method=None):
            self.method = method

        def __call__(self, *args, **kwargs):
            if not self.method:
                raise Render.NoRenderMethod()
            return self.method.__call__(*args, **kwargs)

    def __init__(self, method=None):
        self.render_method = self.RenderMethod(method)
        self.result = None

    def render(self, context, iterate=False, **kwargs):
        if iterate:
            res = []
            for ctx in context:
                try:
                    rendered = self.render_method(ctx, **kwargs)
                except Exception as e:
                    log.error('render failed: %s', e)
                    continue

                if rendered:
                    res.append(rendered)

            self.result = res
        else:
            try:
                self.result = self.render_method(context, **kwargs)
            except Exception as e:
                log.error('render failed: %s', e)

        return True


class JinjaRender(Render):

    def __init__(self, template):
        try:
            render_method = jinja2.Template(template).render
            super(self.__class__, self).__init__(render_method)

        except jinja2.exceptions.TemplateSyntaxError as e:
            log.error('jinja2 syntax error: %s', e)

        self.template = template


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
                res = "\n".join(s for s in data)
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
        if data is not None:
            print(self.formatter.output(data))
