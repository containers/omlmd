from __future__ import annotations

import json
import logging
import os
import platform
import tarfile
import typing as t
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


@dataclass
class DeferredLayer:
    src: Path
    dest: Path
    media_type: str
    transform: t.Callable[[], None] | None = None
    owned: bool = True

    def __post_init__(self):
        if self.dest.exists():
            self.owned = False

    @classmethod
    def raw(cls, src: Path, media_type: str) -> DeferredLayer:
        return cls(src, src, media_type)

    @classmethod
    def blob(cls, src: Path, gz: bool = False) -> DeferredLayer:
        oflag = "w"
        media_type = MIME_BLOB
        if gz:
            oflag += ":gz"
            media_type += "+gzip"

        dest = src.with_suffix(".tar")

        def _tar():
            with tarfile.open(dest, oflag) as tf:
                tf.add(src, arcname=src.name)

        return cls(src, dest, media_type, _tar)

    def as_layer(self) -> str:
        if self.owned and self.transform:
            self.transform()
        return f"{self.dest}:{self.media_type}"


def get_arch() -> str:
    mac = platform.machine()
    if mac == "x86_64":
        return "amd64"
    if mac == "arm64" or mac == "aarch64":
        return "arm64"
    msg = f"Unsupported architecture: {mac}"
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
        if meta_path.exists():
            owns_meta = False
            logger.warning("Reusing intermediate metadata files.")
            logger.debug(f"{meta_path}")
            model_metadata = ModelMetadata(**json.loads(meta_path.read_bytes()))
            if kwargs and ModelMetadata.from_dict(kwargs) != model_metadata:
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

        manifest_path = path.parent / "manifest.json"
        model: DeferredLayer | None = None
        meta: DeferredLayer | None = None
        if not as_artifact:
            manifest_path.write_text(
                json.dumps(
                    {
                        "architecture": get_arch(),
                        "os": "linux",
                    }
                )
            )
            config = DeferredLayer.raw(manifest_path, MIME_MANIFEST_CONFIG)
            model = DeferredLayer.blob(path)
            meta = DeferredLayer.blob(meta_path, gz=True)
        else:
            manifest_path.write_text(
                json.dumps(
                    {
                        "artifactType": MIME_APPLICATION_MLMODEL,
                    }
                )
            )
            config = DeferredLayer.raw(manifest_path, MIME_APPLICATION_MLMODEL)
            model = DeferredLayer.raw(path, MIME_APPLICATION_MLMODEL)
            meta = DeferredLayer.raw(meta_path, MIME_APPLICATION_MLMETADATA)
            meta.owned = owns_meta

        layers = [
            config,
            model,
            meta,
        ]
        try:
            result = self._registry.push(
                target=target,
                files=[lay.as_layer() for lay in layers],
                manifest_annotations=model_metadata.to_annotations_dict(),
                manifest_config=config.as_layer(),
                do_chunked=True,
            )
        finally:
            for lay in layers:
                if lay.owned:
                    lay.dest.unlink()
            if owns_meta and meta_path.exists():
                meta_path.unlink()

        self.notify_listeners(PushEvent.from_response(result, target, model_metadata))
        return result

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
