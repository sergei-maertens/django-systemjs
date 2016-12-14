from __future__ import unicode_literals

import hashlib
import io
import json
import logging
import os
import posixpath
import subprocess

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.encoding import force_text

import semantic_version

from .jspm import locate_package_json

logger = logging.getLogger(__name__)


JSPM_LOG_VERSION = semantic_version.Version('0.16.3')

SOURCEMAPPING_URL_COMMENT = b'//# sourceMappingURL='

NODE_ENV_VAR = 'NODE_PATH'


class BundleError(OSError):
    pass


class System(object):

    def __init__(self, **opts):
        self.opts = opts
        self.stdout = self.stdin = self.stderr = subprocess.PIPE
        self.cwd = None
        self.version = None  # JSPM version

    def _has_jspm_log(self):
        return self.jspm_version and self.jspm_version >= JSPM_LOG_VERSION

    def get_jspm_version(self, opts):
        jspm_bin = opts['jspm']
        cmd = '{} --version'.format(jspm_bin)
        proc = subprocess.Popen(
            cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
            stdin=self.stdin, stderr=self.stderr)
        result, err = proc.communicate()  # block until it's done
        if err:
            raise BundleError("Could not determine JSPM version, error: %s", err)
        version_string = result.decode().split()[0]
        return semantic_version.Version(version_string, partial=True)

    @property
    def jspm_version(self):
        if not self.version:
            options = self.opts.copy()
            options.setdefault('jspm', settings.SYSTEMJS_JSPM_EXECUTABLE)
            self.version = self.get_jspm_version(options)
        return self.version

    def bundle(self, app):
        bundle = SystemBundle(self, app, **self.opts)
        return bundle.bundle()

    @staticmethod
    def get_bundle_path(app):
        """
        Returns the path relative to STATIC_URL for the bundle for app.
        """
        bundle = SystemBundle(None, app)
        return bundle.get_paths()[1]


class SystemBundle(object):
    """
    Represents a single app to be bundled.
    """

    def __init__(self, system, app, **options):
        """
        Initialize a SystemBundle object.

        :param system: a System instance that holds the non-bundle specific
        meta information (such as jspm version, configuration)

        :param app: string, the name of the JS package to bundle. This may be
        missing the '.js' extension.

        :param options: dict containing the bundle-specific options. Possible
        options:
            `jspm`: `jspm` executable (if it's not on $PATH, for example)
            `log`: logging mode for jspm, can be ok|warn|err. Only available
                   for jspm >= 0.16.3
            `minify`: boolean, whether go generate minified bundles or not
            `sfx`: boolean, generate a self-executing bundle or not
            `skip-source-maps: boolean, whether to generate source maps or not
        """
        self.system = system
        self.app = app

        # set the bundle options
        options.setdefault('jspm', settings.SYSTEMJS_JSPM_EXECUTABLE)
        self.opts = options

        bundle_cmd = self.get_bundle_sfx_cmd() if self.opts.get('sfx') else 'bundle'
        self.command = '{jspm} ' + bundle_cmd + ' {app} {outfile}'

        self.stdout = self.stdin = self.stderr = subprocess.PIPE

    def get_bundle_sfx_cmd(self):
        spec = semantic_version.Spec('>=0.17.0')
        return 'build' if self.system.jspm_version in spec else 'bundle-sfx'

    def get_outfile(self):
        js_file = '{app}{ext}'.format(app=self.app, ext='.js' if self.needs_ext() else '')
        outfile = os.path.join(settings.STATIC_ROOT, settings.SYSTEMJS_OUTPUT_DIR, js_file)
        return outfile

    def get_paths(self):
        """
        Return a tuple with the absolute path and relative path (relative to STATIC_URL)
        """
        outfile = self.get_outfile()
        rel_path = os.path.relpath(outfile, settings.STATIC_ROOT)
        return outfile, rel_path

    def needs_ext(self):
        """
        Check whether `self.app` is missing the '.js' extension and if it needs it.
        """
        if settings.SYSTEMJS_DEFAULT_JS_EXTENSIONS:
            name, ext = posixpath.splitext(self.app)
            if not ext:
                return True
        return False

    def bundle(self):
        """
        Bundle the app and return the static url to the bundle.
        """
        outfile, rel_path = self.get_paths()

        options = self.opts
        if self.system._has_jspm_log():
            self.command += ' --log {log}'
            options.setdefault('log', 'err')

        if options.get('minify'):
            self.command += ' --minify'

        if options.get('skip_source_maps'):
            self.command += ' --skip-source-maps'

        try:
            cmd = self.command.format(app=self.app, outfile=outfile, **options)
            proc = subprocess.Popen(
                cmd, shell=True, cwd=self.system.cwd, stdout=self.stdout,
                stdin=self.stdin, stderr=self.stderr)

            result, err = proc.communicate()  # block until it's done
            if err and self.system._has_jspm_log():
                fmt = 'Could not bundle \'%s\': \n%s'
                logger.warn(fmt, self.app, err)
                raise BundleError(fmt % (self.app, err))
            if result.strip():
                logger.info(result)
        except (IOError, OSError) as e:
            if isinstance(e, BundleError):
                raise
            raise BundleError('Unable to apply %s (%r): %s' % (
                              self.__class__.__name__, cmd, e))
        else:
            if not options.get('sfx'):
                # add the import statement, which is missing for non-sfx bundles
                sourcemap = find_sourcemap_comment(outfile)
                with open(outfile, 'a') as of:
                    of.write("\nSystem.import('{app}{ext}');\n{sourcemap}".format(
                        app=self.app,
                        ext='.js' if self.needs_ext() else '',
                        sourcemap=sourcemap if sourcemap else '',
                    ))
        return rel_path


class TraceError(Exception):
    pass


class SystemTracer(object):

    def __init__(self, node_path=None):
        node_env = os.environ.copy()
        if node_path and NODE_ENV_VAR not in node_env:
            node_env[NODE_ENV_VAR] = node_path
        self.env = node_env
        self.name = 'deps.json'
        self.storage = staticfiles_storage
        self._trace_cache = {}
        self._package_json_dir = os.path.dirname(locate_package_json())

    @property
    def cache_file_path(self):
        if not os.path.exists(settings.SYSTEMJS_CACHE_DIR):
            os.makedirs(settings.SYSTEMJS_CACHE_DIR)
        return os.path.join(settings.SYSTEMJS_CACHE_DIR, self.name)

    def trace(self, app):
        """
        Trace the dependencies for app.

        A tracer-instance is shortlived, and re-tracing the same app should
        yield the same results. Since tracing is an expensive process, cache
        the result on the tracer instance.
        """
        if app not in self._trace_cache:
            process = subprocess.Popen(
                "trace-deps.js {}".format(app), shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=self.env, universal_newlines=True, cwd=self._package_json_dir
            )
            out, err = process.communicate()
            if err:
                raise TraceError(err)
            self._trace_cache[app] = json.loads(out)
        return self._trace_cache[app]

    def get_hash(self, path):
        md5 = hashlib.md5()
        with self.storage.open(path) as infile:
            for chunk in infile.chunks():
                md5.update(chunk)
        return md5.hexdigest()

    def write_depcache(self, app_deps, bundle_options):  # TODO: use storage
        all_deps = {
            'version': 1,
            'packages': app_deps,
            'hashes': {},
            'options': bundle_options,
        }

        for pkg_deptree in app_deps.values():
            for module, info in pkg_deptree.items():
                # issue #13 - external resources are not included in the bundle,
                # so don't include them in the depcache either
                if info.get('skip', False):
                    continue
                path = info['path']
                if path not in all_deps['hashes']:
                    all_deps['hashes'][path] = self.get_hash(path)

        with open(self.cache_file_path, 'w') as outfile:
            json.dump(all_deps, outfile)

    @property
    def cached_deps(self):
        if not hasattr(self, '_depcache'):
            with open(self.cache_file_path, 'r') as infile:
                self._depcache = json.load(infile)
        return self._depcache

    def get_depcache(self, app):
        # cache in memory for faster lookup
        if self.cached_deps.get('version') == 1:
            return self.cached_deps['packages'].get(app)
        else:
            raise NotImplementedError  # noqa

    def get_hashes(self):
        if self.cached_deps.get('version') == 1:
            return self.cached_deps['hashes']
        else:
            raise NotImplementedError  # noqa

    def get_bundle_options(self):
        if self.cached_deps.get('version') == 1:
            return self.cached_deps.get('options')
        else:
            raise NotImplementedError  # noqa

    def hashes_match(self, dep_tree):
        """
        Compares the app deptree file hashes with the hashes stored in the
        cache.
        """
        hashes = self.get_hashes()
        for module, info in dep_tree.items():
            md5 = self.get_hash(info['path'])
            if md5 != hashes[info['path']]:
                return False
        return True

    def check_needs_update(self, app):
        cached_deps = self.get_depcache(app)
        deps = self.trace(app)
        # no re-bundle needed if the trees, mtimes and file hashes match
        if deps == cached_deps and self.hashes_match(deps):
            return False
        return True


def find_sourcemap_comment(filepath, block_size=100):
    """
    Seeks and removes the sourcemap comment. If found, the sourcemap line is
    returned.

    Bundled output files can have massive amounts of lines, and the sourceMap
    comment is always at the end. So, to extract it efficiently, we read out the
    lines of the file starting from the end. We look back at most 2 lines.

    :param:filepath: path to output bundle file containing the sourcemap comment
    :param:blocksize: integer saying how many bytes to read at once
    :return:string with the sourcemap comment or None
    """

    MAX_TRACKBACK = 2  # look back at most 2 lines, catching potential blank line at the end

    block_number = -1
    # blocks of size block_size, in reverse order starting from the end of the file
    blocks = []
    sourcemap = None

    try:
        # open file in binary read+write mode, so we can seek with negative offsets
        of = io.open(filepath, 'br+')
        # figure out what's the end byte
        of.seek(0, os.SEEK_END)
        block_end_byte = of.tell()

        # track back for maximum MAX_TRACKBACK lines and while we can track back
        while block_end_byte > 0 and MAX_TRACKBACK > 0:
            if (block_end_byte - block_size > 0):
                # read the last block we haven't yet read
                of.seek(block_number*block_size, os.SEEK_END)
                blocks.append(of.read(block_size))
            else:
                # file too small, start from begining
                of.seek(0, os.SEEK_SET)
                # only read what was not read
                blocks = [of.read(block_end_byte)]

            # update variables that control while loop
            content = b''.join(reversed(blocks))
            lines_found = content.count(b'\n')
            MAX_TRACKBACK -= lines_found
            block_end_byte -= block_size
            block_number -= 1

            # early check and bail out if we found the sourcemap comment
            if SOURCEMAPPING_URL_COMMENT in content:
                offset = 0
                # splitlines eats the last \n if its followed by a blank line
                lines = content.split(b'\n')
                for i, line in enumerate(lines):
                    if line.startswith(SOURCEMAPPING_URL_COMMENT):
                        offset = len(line)
                        sourcemap = line
                        break
                while i+1 < len(lines):
                    offset += 1  # for the newline char
                    offset += len(lines[i+1])
                    i += 1
                # track back until the start of the comment, and truncate the comment
                if sourcemap:
                    offset += 1  # for the newline before the sourcemap comment
                    of.seek(-offset, os.SEEK_END)
                    of.truncate()
                return force_text(sourcemap)
    finally:
        of.close()
    return sourcemap
