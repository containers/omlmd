from dataclasses import fields
from typing import Optional, List
from omlmd.model_metadata import ModelMetadata
from omlmd.provider import OMLMDRegistry
import os
import urllib.request

def write_content_to_file(filename: str, content_fn):
    try:
        with open(filename, 'x') as f:
            content = content_fn()
            f.write(content)
    except FileExistsError:
        raise RuntimeError(f"File '{filename}' already exists. Aborting TODO: demonstrator.")


def download_file(uri):
    file_name = os.path.basename(uri)
    urllib.request.urlretrieve(uri, file_name)
    return file_name


class Helper:
    def __init__(self, registry: Optional[OMLMDRegistry] = None):
        if registry is None:
            self._registry = OMLMDRegistry(insecure=True) # TODO: this is a bit limiting when used from CLI, to be refactored
        else:
            self._registry = registry

    @property
    def registry(self):
        return self._registry

    def push(
        self,
        target: str,
        path: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        model_format_name: Optional[str] = None,
        model_format_version: Optional[str] = None,
        **kwargs
    ):
        dataclass_fields = {f.name for f in fields(ModelMetadata)} # avoid anything specified in kwargs which would collide
        custom_properties = {k: v for k, v in kwargs.items() if k not in dataclass_fields}
        model_metadata = ModelMetadata(
            name=name,
            description=description,
            author=author,
            customProperties=custom_properties,
            model_format_name=model_format_name,
            model_format_version=model_format_version
        )
        write_content_to_file("model_metadata.omlmd.json", lambda: model_metadata.to_json())
        write_content_to_file("model_metadata.omlmd.yaml", lambda: model_metadata.to_yaml())
        files = [
            f"{path}:application/x-mlmodel",
            "model_metadata.omlmd.json:application/x-config",
            "model_metadata.omlmd.yaml:application/x-config",
        ]
        try:
            # print(target, files, model_metadata.to_annotations_dict())
            return self._registry.push(
                target=target,
                files=files,
                manifest_annotations=model_metadata.to_annotations_dict(),
                manifest_config="model_metadata.omlmd.json:application/x-config"
            )
        finally:
            os.remove("model_metadata.omlmd.json")
            os.remove("model_metadata.omlmd.yaml")


    def pull(
        self,
        target: str,
        outdir: str,
        media_types: Optional[List[str]] = None
    ):
        self._registry.download_layers(target, outdir, media_types)


    def get_config(
        self,
        target: str
    ) -> str:
        return f'{{"reference":"{target}", "config": {self._registry.get_config(target)} }}' # this assumes OCI Manifest.Config later is JSON (per std spec)


    def crawl(
        self,
        targets: List[str]
    ) -> str:
        configs = map(self.get_config, targets)
        joined = "[" + ", ".join(configs) + "]"
        return joined
