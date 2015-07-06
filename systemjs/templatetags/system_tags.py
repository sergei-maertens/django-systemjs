import os
import subprocess

from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

from systemjs.conf import settings

register = template.Library()


class System(object):

    def __init__(self, app, **opts):
        self.app = app
        self.opts = opts
        self.stdout = self.stdin = self.stderr = subprocess.PIPE
        self.cwd = None

    def get_outfile(self):
        self.js_file = u'{app}.js'.format(app=self.app)
        outfile = os.path.join(settings.STATIC_ROOT, settings.SYSTEMJS_OUTPUT_DIR, self.js_file)
        return outfile

    def command(self, command):
        """
        Bundle the app and return the static url to the bundle.
        """
        outfile = self.get_outfile()
        rel_path = os.path.relpath(outfile, settings.STATIC_ROOT)
        check_existing = self.opts.get('check', False)
        force = self.opts.get('force', False)
        if force or (check_existing and not os.path.exists(outfile)):
            options = self.opts.copy()
            options.setdefault('jspm', settings.SYSTEMJS_JSPM_EXECUTABLE)
            try:
                cmd = command.format(app=self.app, outfile=outfile, **options)
                proc = subprocess.Popen(
                    cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
                    stdin=self.stdin, stderr=self.stderr)
                result, err = proc.communicate()  # block until it's done
                # TODO: do something with result/err
            except (IOError, OSError) as e:
                raise OSError('Unable to apply %s (%r): %s' %
                              (self.__class__.__name__, command, e))
        return rel_path

    @classmethod
    def bundle(cls, app, **opts):
        system = cls(app, **opts)
        cmd = u'{jspm} bundle-sfx {app} {outfile}'
        return system.command(cmd)


class SystemImportNode(template.Node):

    def __init__(self, path):
        self.path = path

    def render(self, context):
        """
        Build the filepath by appending the extension.
        """
        module_path = self.path.resolve(context)
        if not settings.SYSTEMJS_ENABLED:
            tpl = """<script type="text/javascript">System.import('{app}');</script>"""
            return tpl.format(app=module_path)

        # else: create a bundle
        rel_path = System.bundle(module_path)
        url = staticfiles_storage.url(rel_path)
        return """<script type="text/javascript" src="{url}"></script>""".format(url=url)

    @classmethod
    def handle_token(cls, parser, token):
        bits = token.split_contents()

        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes at least one argument (js module, without extension)" % bits[0])

        # for 'as varname' support, check django.templatetags.static
        path = parser.compile_filter(bits[1])
        return cls(path)


@register.tag
def systemjs_import(parser, token):
    """
    Import a Javascript module via SystemJS, bundling the app.

    Syntax::

        {% system_import 'path/to/file' %}

    Example::

        {% system_import 'mydjangoapp/js/myapp' %}

    Which would be rendered like::

        <script type="text/javascript" src="/static/CACHE/mydjangoapp.js.min.myapp.js"></script>

    where /static/CACHE can be configured through settings.

    In DEBUG mode, the result would be

        <script type="text/javascript">System.import('mydjangoapp/js/myapp');</script>
    """

    return SystemImportNode.handle_token(parser, token)
