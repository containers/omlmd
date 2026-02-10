from __future__ import annotations

import logging
import os
import tempfile

from oras import provider
from oras.decorator import ensure_container
from oras.defaults import annotation_title as ANNOTATION_TITLE
from oras.utils import sanitize_path

logger = logging.getLogger(__name__)


class OMLMDRegistry(provider.Registry):
    @ensure_container
    def download_layers(self, package, download_dir, media_types):
        """
        Given a manifest of layers, retrieve a layer based on desired media type
        """
        # If you intend to call this function again, you might cache this response
        # for the package of interest.
        manifest = self.get_manifest(package)

        paths = []

        for layer in manifest.get("layers", []):
            if (
                media_types is None
                or len(media_types) == 0
                or layer["mediaType"] in media_types
            ):
                artifact = layer["annotations"][ANNOTATION_TITLE]
                outfile = sanitize_path(
                    download_dir, os.path.join(download_dir, artifact)
                )
                path = self.download_blob(package, layer["digest"], outfile)
                paths.append(path)

        return paths

    @ensure_container
    def get_config(self, package) -> str:
        """
        Given a manifest of layers, retrieve a layer based on desired media type
        """
        # If you intend to call this function again, you might cache this response
        # for the package of interest.
        manifest = self.get_manifest(package)

        manifest_config = manifest.get("config", {})

        for layer in manifest.get("layers", []):
            if layer["digest"] == manifest_config["digest"]:
                temp_dir = tempfile.mkdtemp()
                try:
                    with tempfile.NamedTemporaryFile(
                        dir=temp_dir, delete=False
                    ) as temp_file:
                        self.download_blob(package, layer["digest"], temp_file.name)
                    with open(temp_file.name, "r") as temp_file_read:
                        file_content = temp_file_read.read()
                        return file_content
                finally:
                    if os.path.exists(temp_dir):
                        for root, dirs, files in os.walk(temp_dir, topdown=False):
                            for file in files:
                                os.remove(os.path.join(root, file))
                            for dir in dirs:
                                os.rmdir(os.path.join(root, dir))
                        os.rmdir(temp_dir)
                        # print("Temporary directory and its contents have been removed.")
        raise RuntimeError("Unable to locate config layer")
