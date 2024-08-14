from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Any

import yaml


@dataclass
class ModelMetadata:
    name: str | None = None
    description: str | None = None
    author: str | None = None
    customProperties: dict[str, Any] | None = field(default_factory=dict)
    uri: str | None = None
    model_format_name: str | None = None
    model_format_version: str | None = None

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_annotations_dict(self) -> dict[str, str]:
        as_dict = self.to_dict()
        result = {}
        # TODO: likely key in annotation require FQDN
        for k, v in as_dict.items():
            if isinstance(v, str):
                result[k] = v
            elif v is None:
                continue
            else:
                result[f"{k}+json"] = json.dumps(
                    v
                )  # post-fix "+json" for OCI annotation which is a str representing a json
        return result

    @staticmethod
    def from_json(json_str: str) -> "ModelMetadata":
        data = json.loads(json_str)
        return ModelMetadata(**data)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False)

    @staticmethod
    def from_yaml(yaml_str: str) -> "ModelMetadata":
        data = yaml.safe_load(yaml_str)
        return ModelMetadata(**data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ModelMetadata":
        known_keys = {f.name for f in fields(ModelMetadata)}
        known_properties = {key: data.get(key) for key in known_keys if key in data}
        custom_properties = {
            key: value for key, value in data.items() if key not in known_keys
        }

        return ModelMetadata(**known_properties, customProperties=custom_properties)


def deserialize_mdfile(file):
    with open(file, "r") as file:
        content = file.read()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        pass

    raise ValueError(
        f"The file at {file} is neither a valid JSON nor a valid YAML file."
    )
