import json

from django.conf import settings
from django.contrib.staticfiles.storage import FileSystemStorage, ManifestStaticFilesStorage
from django.core.files.base import ContentFile
from django.core.management import CommandError


class SystemJSManifestStaticFilesMixin(object):
    """
    Do not delete the old manifest, but append to it.
    """

    systemjs_bundling = False

    systemjs_manifest_name = 'systemjs.json'

    def save_systemjs_manifest(self, bundle_files):
        payload = {'paths': bundle_files, 'version': self.manifest_version}
        contents = json.dumps(payload).encode('utf-8')
        self._save(self.systemjs_manifest_name, ContentFile(contents))

    def load_systemjs_manifest(self):
        """
        Load the existing systemjs manifest and remove any entries that no longer
        exist on the storage.
        """
        # backup the original name
        _manifest_name = self.manifest_name

        # load the custom bundle manifest
        self.manifest_name = self.systemjs_manifest_name
        bundle_files = self.load_manifest()
        # reset the manifest name
        self.manifest_name = _manifest_name

        # check that the files actually exist, if not, remove them from the manifest
        for file, hashed_file in bundle_files.copy().items():
            if not self.exists(file) or not self.exists(hashed_file):
                del bundle_files[file]
        return bundle_files

    def save_manifest(self):
        # load the systemjs manifest
        bundle_files = self.load_systemjs_manifest()

        if self.systemjs_bundling:
            if not self.exists(self.manifest_name):
                raise CommandError('You need to run collectstatic first')
            # update the systemjs manifest with the bundle hashes
            bundle_files.update(self.hashed_files)
            if self.exists(self.systemjs_manifest_name):
                self.delete(self.systemjs_manifest_name)
            self.save_systemjs_manifest(bundle_files)
            # load the existing manifest
            hashed_files = self.load_manifest()
        else:  # regular collectstatic behaviour - add the bundle manifest
            self.hashed_files.update(bundle_files)

        super(SystemJSManifestStaticFilesMixin, self).save_manifest()

        # the default has now removed the manifest, and overwritten the new version
        if self.systemjs_bundling:
            # add to hashed_files
            hashed_files.update(bundle_files)
            payload = {'paths': hashed_files, 'version': self.manifest_version}
            contents = json.dumps(payload).encode('utf-8')
            self.delete(self.manifest_name)  # delete old file
            self._save(self.manifest_name, ContentFile(contents))


class SystemJSManifestStaticFilesStorage(SystemJSManifestStaticFilesMixin, ManifestStaticFilesStorage):
    pass


class JSPMFileStorage(FileSystemStorage):

    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL
        super(JSPMFileStorage, self).__init__(location, base_url, *args, **kwargs)
