import json

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.core.files.base import ContentFile
from django.core.management import CommandError


class SystemJSManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Do not delete the old manifest, but append to it.
    """

    systemjs_bundling = False

    def save_manifest(self):
        if not self.exists(self.manifest_name):
            raise CommandError('You need to run collectstatic first')

        if self.systemjs_bundling:
            # load the result of collectstatic before it's overwritten
            hashed_files = self.load_manifest()

        super(SystemJSManifestStaticFilesStorage, self).save_manifest()
        if not self.systemjs_bundling:
            return

        # add to hashed_files
        hashed_files.update(self.hashed_files)
        payload = {'paths': hashed_files, 'version': self.manifest_version}
        contents = json.dumps(payload).encode('utf-8')
        self._save(self.manifest_name, ContentFile(contents))
