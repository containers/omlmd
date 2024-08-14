from __future__ import annotations

import os
import urllib.request
from dataclasses import fields

from omlmd.listener import Event, Listener, PushEvent
from omlmd.model_metadata import ModelMetadata
from omlmd.provider import OMLMDRegistry


def write_content_to_file(filename: str, content_fn):
    try:
        with open(filename, "x") as f:
            content = content_fn()
            f.write(content)
    except FileExistsError:
        raise RuntimeError(
            f"File '{filename}' already exists. Aborting TODO: demonstrator."
        )


def download_file(uri):
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
        path: str,
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
        write_content_to_file(
            "model_metadata.omlmd.json", lambda: model_metadata.to_json()
        )
        write_content_to_file(
            "model_metadata.omlmd.yaml", lambda: model_metadata.to_yaml()
        )
        files = [
            f"{path}:application/x-mlmodel",
            "model_metadata.omlmd.json:application/x-config",
            "model_metadata.omlmd.yaml:application/x-config",
        ]
        try:
            # print(target, files, model_metadata.to_annotations_dict())
            result = self._registry.push(
                target=target,
                files=files,
                manifest_annotations=model_metadata.to_annotations_dict(),
                manifest_config="model_metadata.omlmd.json:application/x-config",
            )
            self.notify_listeners(PushEvent(target, model_metadata))
            return result
        finally:
            os.remove("model_metadata.omlmd.json")
            os.remove("model_metadata.omlmd.yaml")

    def pull(self, target: str, outdir: str, media_types: list[str] | None = None):
        self._registry.download_layers(target, outdir, media_types)

    def get_config(self, target: str) -> str:
        return f'{{"reference":"{target}", "config": {self._registry.get_config(target)} }}'  # this assumes OCI Manifest.Config later is JSON (per std spec)

    def crawl(self, targets: list[str]) -> str:
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
