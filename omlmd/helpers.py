from __future__ import annotations

import logging
import os
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent

from .constants import (
    FILENAME_METADATA_JSON,
    MIME_APPLICATION_CONFIG,
    MIME_APPLICATION_MLMODEL,
)
from .listener import Event, Listener, PushEvent
from .model_metadata import ModelMetadata
from .provider import OMLMDRegistry

logger = logging.getLogger(__name__)


def download_file(uri: str):
    file_name = os.path.basename(uri)
    urllib.request.urlretrieve(uri, file_name)
    return file_name


@dataclass
class Helper:
    _registry: OMLMDRegistry = field(
        default_factory=lambda: OMLMDRegistry(insecure=True)
    )
    _listeners: list[Listener] = field(default_factory=list)

    @classmethod
    def from_default_registry(cls, insecure: bool):
        return cls(OMLMDRegistry(insecure=insecure))

    def push(
        self,
        target: str,
        path: Path | str,
        **kwargs,
    ):
        owns_meta = True
        if isinstance(path, str):
            path = Path(path)

        meta_path = path.parent / FILENAME_METADATA_JSON
        if not kwargs and meta_path.exists():
            owns_meta = False
            logger.warning("Reusing intermediate metadata files.")
            logger.debug(f"{meta_path}")
            with open(meta_path, "r") as f:
                model_metadata = ModelMetadata.from_json(f.read())
        elif meta_path.exists():
            err = dedent(f"""
OMLMD intermediate metadata files found at '{meta_path}'.
Cannot resolve with conflicting keyword args: {kwargs}.
You can reuse the existing metadata by omitting any keywords.
If that was NOT intended, please REMOVE that file from your environment before re-running.

Note for advanced users: if merging keys with existing metadata is desired, you should create a Feature Request upstream: https://github.com/containers/omlmd""")
            raise RuntimeError(err)
        else:
            model_metadata = ModelMetadata.from_dict(kwargs)
            meta_path.write_text(model_metadata.to_json())

        config = f"{meta_path}:{MIME_APPLICATION_CONFIG}"
        files = [
            f"{path}:{MIME_APPLICATION_MLMODEL}",
            config,
        ]
        try:
            # print(target, files, model_metadata.to_annotations_dict())
            result = self._registry.push(
                target=target,
                files=files,
                manifest_annotations=model_metadata.to_annotations_dict(),
                manifest_config=config,
                do_chunked=True,
            )
            self.notify_listeners(
                PushEvent.from_response(result, target, model_metadata)
            )
            return result
        finally:
            if owns_meta:
                meta_path.unlink()

    def pull(
        self, target: str, outdir: Path | str, media_types: Sequence[str] | None = None
    ):
        self._registry.download_layers(target, outdir, media_types)

    def get_config(self, target: str) -> str:
        return f'{{"reference":"{target}", "config": {self._registry.get_config(target)} }}'  # this assumes OCI Manifest.Config later is JSON (per std spec)

    def crawl(self, targets: Sequence[str]) -> str:
        configs = map(self.get_config, targets)
        joined = "[" + ", ".join(configs) + "]"
        return joined

    def add_listener(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: Listener) -> None:
        self._listeners.remove(listener)

    def notify_listeners(self, event: Event) -> None:
        for listener in self._listeners:
            listener.update(self, event)
