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

    def save_manifest(self):
        if self.systemjs_bundling:
            if not self.exists(self.manifest_name):
                raise CommandError('You need to run collectstatic first')
            # load the result of collectstatic before it's overwritten
            hashed_files = self.load_manifest()

        super(SystemJSManifestStaticFilesMixin, self).save_manifest()
        if not self.systemjs_bundling:
            return

        # add to hashed_files
        hashed_files.update(self.hashed_files)
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
