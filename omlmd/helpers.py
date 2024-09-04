from __future__ import annotations

import logging
import os
import urllib.request
from collections.abc import Sequence
from dataclasses import fields
from pathlib import Path

from omlmd.constants import (
    FILENAME_METADATA_JSON,
    FILENAME_METADATA_YAML,
    MIME_APPLICATION_CONFIG,
    MIME_APPLICATION_MLMODEL,
)
from omlmd.listener import Event, Listener, PushEvent
from omlmd.model_metadata import ModelMetadata
from omlmd.provider import OMLMDRegistry


logger = logging.getLogger(__name__)


def download_file(uri: str):
    file_name = os.path.basename(uri)
    urllib.request.urlretrieve(uri, file_name)
    return file_name


class Helper:
    _listeners: list[Listener] = []

    def __init__(self, registry: OMLMDRegistry | None = None):
        if registry is None:
            self._registry = OMLMDRegistry(
                insecure=True
            )  # TODO: this is a bit limiting when used from CLI, to be refactored
        else:
            self._registry = registry

    @property
    def registry(self):
        return self._registry

    def push(
        self,
        target: str,
        path: Path | str,
        name: str | None = None,
        description: str | None = None,
        author: str | None = None,
        model_format_name: str | None = None,
        model_format_version: str | None = None,
        **kwargs,
    ):
        dataclass_fields = {
            f.name for f in fields(ModelMetadata)
        }  # avoid anything specified in kwargs which would collide
        custom_properties = {
            k: v for k, v in kwargs.items() if k not in dataclass_fields
        }
        model_metadata = ModelMetadata(
            name=name,
            description=description,
            author=author,
            customProperties=custom_properties,
            model_format_name=model_format_name,
            model_format_version=model_format_version,
        )
        owns_meta_files = True
        if isinstance(path, str):
            path = Path(path)

        json_meta = path.parent / FILENAME_METADATA_JSON
        yaml_meta = path.parent / FILENAME_METADATA_YAML
        if model_metadata.is_empty() and json_meta.exists() and yaml_meta.exists():
            owns_meta_files = False
            logger.warning("No metadata supplied, but reusing md files found in path.")
            logger.debug(f"{json_meta}, {yaml_meta}")
            with open(json_meta, "r") as f:
                model_metadata = ModelMetadata.from_json(f.read())
        elif (p := json_meta).exists() or (p := yaml_meta).exists():
            raise RuntimeError(
                f"File '{p}' already exists. Aborting TODO: demonstrator."
            )
        else:
            json_meta.write_text(model_metadata.to_json())
            yaml_meta.write_text(model_metadata.to_yaml())

        manifest_cfg = f"{json_meta}:{MIME_APPLICATION_CONFIG}"
        files = [
            f"{path}:{MIME_APPLICATION_MLMODEL}",
            manifest_cfg,
            f"{yaml_meta}:{MIME_APPLICATION_CONFIG}",
        ]
        try:
            # print(target, files, model_metadata.to_annotations_dict())
            result = self._registry.push(
                target=target,
                files=files,
                manifest_annotations=model_metadata.to_annotations_dict(),
                manifest_config=manifest_cfg,
                do_chunked=True,
            )
            self.notify_listeners(PushEvent(target, model_metadata))
            return result
        finally:
            if owns_meta_files:
                json_meta.unlink()
                yaml_meta.unlink()

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
