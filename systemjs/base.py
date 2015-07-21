from __future__ import unicode_literals

import os
import subprocess

from .conf import settings


class BundleError(OSError):
    pass


class System(object):

    def __init__(self, app, **opts):
        self.app = app
        self.opts = opts
        self.stdout = self.stdin = self.stderr = subprocess.PIPE
        self.cwd = None
        self.sfx = opts.pop('sfx', False)

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
                raise BundleError('Unable to apply %s (%r): %s' %
                                  (self.__class__.__name__, command, e))
            else:
                if not self.sfx:
                    # add the import statement, which is missing for non-sfx bundles
                    with open(outfile, 'w') as of:
                        of.write("\nSystem.import('{app}');\n".format(app=self.app))
        return rel_path

    @classmethod
    def bundle(cls, app, sfx=False, **opts):
        system = cls(app, sfx=sfx, **opts)
        bundle_cmd = 'bundle-sfx' if sfx else 'bundle'
        cmd = u'{jspm} ' + bundle_cmd + ' {app} {outfile}'
        return system.command(cmd)
