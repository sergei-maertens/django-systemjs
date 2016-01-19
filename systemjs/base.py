from __future__ import unicode_literals

import logging
import os
import posixpath
import subprocess

from .conf import settings


JSPM_LOG_VERSION = (0, 16, 3)

logger = logging.getLogger(__name__)


class BundleError(OSError):
    pass


class System(object):

    def __init__(self, app, **opts):
        self.app = app
        self.opts = opts
        self.stdout = self.stdin = self.stderr = subprocess.PIPE
        self.cwd = None
        self.sfx = opts.pop('sfx', False)
        self.version = None  # JSPM version

    def _has_jspm_log(self):
        return self.version and self.version >= JSPM_LOG_VERSION

    def get_outfile(self):
        hasext = True
        if settings.SYSTEMJS_DEFAULT_JS_EXTENSIONS:
            name, ext = posixpath.splitext(self.app)
            if not ext:
                hasext = False
        self.js_file = '{app}{ext}'.format(app=self.app, ext='.js' if not hasext else '')
        outfile = os.path.join(settings.STATIC_ROOT, settings.SYSTEMJS_OUTPUT_DIR, self.js_file)
        return outfile

    def get_jspm_version(self, opts):
        jspm_bin = opts['jspm']
        cmd = '{} --version'.format(jspm_bin)
        proc = subprocess.Popen(
            cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
            stdin=self.stdin, stderr=self.stderr)
        result, err = proc.communicate()  # block until it's done
        if err:
            raise BundleError("Could not determine JSPM version, error: %s", err)
        version_string = result.split()[0].decode()
        return tuple([int(x) for x in version_string.split('.')])

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
            if not self.version:
                self.version = self.get_jspm_version(options)
            try:
                if self._has_jspm_log():
                    command += ' --log {log}'
                    options.setdefault('log', 'err')

                cmd = command.format(app=self.app, outfile=outfile, **options)
                proc = subprocess.Popen(
                    cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
                    stdin=self.stdin, stderr=self.stderr)

                result, err = proc.communicate()  # block until it's done
                if err and self._has_jspm_log():
                    fmt = 'Could not bundle \'%s\': \n%s'
                    logger.warn(fmt, self.app, err)
                    raise BundleError(fmt % (self.app, err))
                if result:
                    logger.info(result)
            except (IOError, OSError) as e:
                if isinstance(e, BundleError):
                    raise
                raise BundleError('Unable to apply %s (%r): %s' % (
                                  self.__class__.__name__, cmd, e))
            else:
                if not self.sfx:
                    # add the import statement, which is missing for non-sfx bundles
                    with open(outfile, 'a') as of:
                        of.write("\nSystem.import('{app}.js');\n".format(app=self.app))
        return rel_path

    @classmethod
    def bundle(cls, app, sfx=False, **opts):
        system = cls(app, sfx=sfx, **opts)
        bundle_cmd = 'bundle-sfx' if sfx else 'bundle'
        cmd = '{jspm} ' + bundle_cmd + ' {app} {outfile}'
        return system.command(cmd)
