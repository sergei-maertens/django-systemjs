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
        self.version = None  # JSPM version

    def get_outfile(self):
        self.js_file = u'{app}.js'.format(app=self.app)
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
                if self.version >= (0, 16):
                    command += ' --log {log}'
                    options.setdefault('log', 'err')
                cmd = command.format(app=self.app, outfile=outfile, **options)
                proc = subprocess.Popen(
                    cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
                    stdin=self.stdin, stderr=self.stderr)
                result, err = proc.communicate()  # block until it's done
                # TODO: do something with result/err
            except (IOError, OSError) as e:
                raise BundleError('Unable to apply %s (%r): %s',
                                  self.__class__.__name__, command, e)
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
        cmd = u'{jspm} ' + bundle_cmd + ' {app} {outfile}'
        return system.command(cmd)
