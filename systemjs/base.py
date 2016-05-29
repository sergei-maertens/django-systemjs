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

logger = logging.getLogger(__name__)


JSPM_LOG_VERSION = semantic_version.Version('0.16.3')

SOURCEMAPPING_URL_COMMENT = b'//# sourceMappingURL='

NODE_ENV_VAR = 'NODE_PATH'

# TODO: configurable
CACHE_DIR = os.path.join(settings.ROOT_DIR, 'cache', 'systemjs')


class BundleError(OSError):
    pass


class System(object):

    def __init__(self, app, **opts):
        self.app = app
        self.opts = opts
        self.stdout = self.stdin = self.stderr = subprocess.PIPE
        self.cwd = None
        self.sfx = opts.pop('sfx', False)
        self.minify = opts.pop('minify', False)
        self.version = None  # JSPM version

    def _has_jspm_log(self):
        return self.version and self.version >= JSPM_LOG_VERSION

    def needs_ext(self):
        if settings.SYSTEMJS_DEFAULT_JS_EXTENSIONS:
            name, ext = posixpath.splitext(self.app)
            if not ext:
                return True
        return False

    def get_outfile(self):
        self.js_file = '{app}{ext}'.format(app=self.app, ext='.js' if self.needs_ext() else '')
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
        version_string = result.decode().split()[0]
        return semantic_version.Version(version_string, partial=True)

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

                if self.minify:
                    command += ' --minify'

                cmd = command.format(app=self.app, outfile=outfile, **options)
                proc = subprocess.Popen(
                    cmd, shell=True, cwd=self.cwd, stdout=self.stdout,
                    stdin=self.stdin, stderr=self.stderr)

                result, err = proc.communicate()  # block until it's done
                if err and self._has_jspm_log():
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
                if not self.sfx:
                    # add the import statement, which is missing for non-sfx bundles
                    sourcemap = find_sourcemap_comment(outfile)
                    with open(outfile, 'a') as of:
                        of.write("\nSystem.import('{app}{ext}');\n{sourcemap}".format(
                            app=self.app,
                            ext='.js' if self.needs_ext() else '',
                            sourcemap=sourcemap if sourcemap else '',
                        ))
        return rel_path

    @classmethod
    def bundle(cls, app, sfx=False, **opts):
        system = cls(app, sfx=sfx, **opts)
        bundle_cmd = 'bundle-sfx' if sfx else 'bundle'
        cmd = '{jspm} ' + bundle_cmd + ' {app} {outfile}'
        return system.command(cmd)

    @classmethod
    def check_needs_update(cls, app, node_path=None):
        tracer = SystemTracer(node_path=node_path)
        deps = tracer.trace(app)
        cached_deps = tracer.load_depcache(app)
        if deps == cached_deps:
            # mtimes and trees match, check the hashes...
            if tracer.hashes_match(deps):
                return False
        return True


class SystemTracer(object):

    def __init__(self, node_path=None):
        node_env = os.environ.copy()
        if node_path and NODE_ENV_VAR not in node_env:
            node_env[NODE_ENV_VAR] = node_path
        self.env = node_env
        self.name = 'deps.json'
        self.storage = staticfiles_storage

    @property
    def cache_file_path(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        return os.path.join(CACHE_DIR, self.name)

    def trace(self, app):
        process = subprocess.Popen(
            "trace-deps.js {}".format(app), shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=self.env
        )
        out, err = process.communicate()
        return json.loads(out)

    def get_hash(self, path):
        md5 = hashlib.md5()
        with self.storage.open(path) as infile:
            for chunk in infile.chunks():
                md5.update(chunk)
        return md5.hexdigest()

    def write_depcache(self, app_deps):  # TODO: use storage
        all_deps = {
            'version': 1,
            'packages': app_deps,
            'hashes': {}
        }

        for pkg_deptree in app_deps.values():
            for module, info in pkg_deptree.items():
                path = info['path']
                if path not in all_deps['hashes']:
                    all_deps['hashes'][path] = self.get_hash(path)

        with open(self.cache_file_path, 'w') as outfile:
            json.dump(all_deps, outfile)

    def load_depcache(self, app):
        # cache in memory for faster lookup
        if not hasattr(self, '_depcache'):
            with open(self.cache_file_path, 'r') as infile:
                self._depcache = json.load(infile)

        if self._depcache.get('version') == 1:
            return self._depcache['packages'].get(app)

        raise NotImplementedError

    def load_hashes(self):
        if not hasattr(self, '_depcache'):
            with open(self.cache_file_path, 'r') as infile:
                self._depcache = json.load(infile)

        if self._depcache.get('version') == 1:
            return self._depcache['hashes']

        raise NotImplementedError

    def hashes_match(self, dep_tree):
        """
        Compares the app deptree file hashes with the hashes stored in the
        cache.
        """
        hashes = self.load_hashes()
        for module, info in dep_tree.items():
            md5 = self.get_hash(info['path'])
            if md5 != hashes[info['path']]:
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
