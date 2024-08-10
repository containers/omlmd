from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json
import yaml

@dataclass
class ModelMetadata:
    name: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    customProperties: Optional[Dict[str, Any]] = field(default_factory=dict)
    uri: Optional[str] = None
    model_format_name: Optional[str] = None
    model_format_version: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)
    
    def to_dict(self) -> dict[str, Any]:
        as_json = self.to_json()
        return json.loads(as_json)
    
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
                result[f"{k}+json"] = json.dumps(v) # post-fix "+json" for OCI annotation which is a str representing a json
        return result

    @staticmethod
    def from_json(json_str: str) -> 'ModelMetadata':
        data = json.loads(json_str)
        return ModelMetadata(**data)

    def to_yaml(self) -> str:
        return yaml.dump(asdict(self), default_flow_style=False)

    @staticmethod
    def from_yaml(yaml_str: str) -> 'ModelMetadata':
        data = yaml.safe_load(yaml_str)
        return ModelMetadata(**data)


def deserialize_mdfile(file):
    with open(file, 'r') as file:
        content = file.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            pass
        
        raise ValueError(f"The file at {file} is neither a valid JSON nor a valid YAML file.")
