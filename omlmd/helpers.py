from __future__ import annotations

import json
import logging
import os
import platform
import tarfile
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from textwrap import dedent

from .constants import (
    FILENAME_METADATA_JSON,
    MIME_APPLICATION_MLMETADATA,
    MIME_APPLICATION_MLMODEL,
    MIME_BLOB,
    MIME_MANIFEST_CONFIG,
)
from .listener import Event, Listener, PushEvent
from .model_metadata import ModelMetadata
from .provider import OMLMDRegistry

logger = logging.getLogger(__name__)


def get_arch() -> str:
    mac = platform.machine()
    if mac == "x86_64":
        return "amd64"
    if mac == "arm64":
        return "arm64"
    if mac == "aarch64":
        return "arm64"
    msg = f"Unsupported architecture: {platform.machine()}"
    raise NotImplementedError(msg)


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
        as_artifact: bool = False,
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
            model_metadata = ModelMetadata.from_dict(json.loads(meta_path.read_bytes()))
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
            meta_path.write_text(json.dumps(model_metadata.to_dict()))

        owns_model_tar = False
        owns_md_tar = False
        manifest_path = path.parent / "manifest.json"
        model_tar = None
        meta_tar = None
        if not as_artifact:
            manifest_path.write_text(
                json.dumps(
                    {
                        "architecture": get_arch(),
                        "os": "linux",
                    }
                )
            )
            config = f"{manifest_path}:{MIME_MANIFEST_CONFIG}"
            model_tar = path.parent / f"{path.stem}.tar"
            meta_tar = path.parent / f"{meta_path.stem}.tar"
            if not model_tar.exists():
                owns_model_tar = True
                with tarfile.open(model_tar, "w") as tf:
                    tf.add(path, arcname=path.name)
            if not meta_tar.exists():
                owns_md_tar = True
                with tarfile.open(meta_tar, "w:gz") as tf:
                    tf.add(meta_path, arcname=meta_path.name)
            files = [
                f"{model_tar}:{MIME_BLOB}",
                f"{meta_tar}:{MIME_BLOB}+gzip",
            ]
        else:
            manifest_path.write_text(
                json.dumps(
                    {
                        "artifactType": MIME_APPLICATION_MLMODEL,
                    }
                )
            )
            config = f"{manifest_path}:{MIME_APPLICATION_MLMODEL}"
            files = [
                f"{path}:{MIME_APPLICATION_MLMODEL}",
                f"{meta_path}:{MIME_APPLICATION_MLMETADATA}",
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
            if owns_model_tar:
                assert isinstance(model_tar, Path)
                model_tar.unlink()
            if owns_md_tar:
                assert isinstance(meta_tar, Path)
                meta_tar.unlink()

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
