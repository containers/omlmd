import json
import tempfile

import yaml

from omlmd.model_metadata import ModelMetadata, deserialize_mdfile


def test_dry_run_model_metadata_json_yaml_conversions():
    metadata = ModelMetadata(name="Example Model", author="John Doe")
    json_str = json.dumps(metadata.to_dict(), indent=4)
    yaml_str = yaml.dump(metadata.to_dict(), default_flow_style=False)

    print("JSON representation:\n", json_str)
    print("YAML representation:\n", yaml_str)

    metadata_from_json = ModelMetadata(**json.loads(json_str))
    metadata_from_yaml = ModelMetadata(**yaml.safe_load(yaml_str))

    print("Metadata from JSON:\n", metadata_from_json)
    print("Metadata from YAML:\n", metadata_from_yaml)

    assert metadata == metadata_from_json
    assert metadata == metadata_from_yaml


def test_deserialize_file_json():
    md_dict = ModelMetadata(
        name="Example Model",
        author="John Doe",
        model_format_name="onnx",
        model_format_version="1",
        customProperties={"accuracy": 0.987},
    ).to_dict()
    json_str = json.dumps(md_dict)

    with tempfile.NamedTemporaryFile(delete=True, mode="w") as f:
        f.write(json_str)
        f.flush()
        metadata_from_json = deserialize_mdfile(f.name)
        assert md_dict == metadata_from_json


def test_deserialize_file_yaml():
    md_dict = ModelMetadata(
        name="Example Model",
        author="John Doe",
        model_format_name="onnx",
        model_format_version="1",
        customProperties={"accuracy": 0.987},
    ).to_dict()
    yaml_str = yaml.dump(md_dict)

    with tempfile.NamedTemporaryFile(delete=True, mode="w") as f:
        f.write(yaml_str)
        f.flush()
        metadata_from_yaml = deserialize_mdfile(f.name)
        assert md_dict == metadata_from_yaml


def test_from_dict():
    data = {
        "name": "mnist",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": 0.987,
    }
    md = ModelMetadata(
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        customProperties={"accuracy": 0.987},
    )
    assert ModelMetadata.from_dict(data) == md
