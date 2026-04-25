import json
import tempfile

import yaml

from omlmd.model_metadata import ModelMetadata, deserialize_mdfile


def test_dry_run_model_metadata_json_yaml_conversions():
    metadata = ModelMetadata(name="Example Model", author="John Doe")
    json_str = metadata.to_json()
    yaml_str = metadata.to_yaml()

    print("JSON representation:\n", json_str)
    print("YAML representation:\n", yaml_str)

    metadata_from_json = ModelMetadata.from_json(json_str)
    metadata_from_yaml = ModelMetadata.from_yaml(yaml_str)

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


def test_is_empty():
    md = ModelMetadata(
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        customProperties={"accuracy": 0.987},
    )
    assert not md.is_empty()

    md = ModelMetadata()
    assert md.is_empty()

    md = ModelMetadata(
        customProperties={"accuracy": 0.987},
    )
    assert not md.is_empty()

    md = ModelMetadata(
        name="mnist",
    )
    assert not md.is_empty()


def test_to_annotations_dict_skips_empty_custom_properties():
    """Issue #18: empty customProperties should not produce an annotation."""
    md = ModelMetadata(name="test-model", customProperties={})
    annotations = md.to_annotations_dict()
    assert "name" in annotations
    assert "customProperties+json" not in annotations


def test_to_annotations_dict_includes_non_empty_custom_properties():
    md = ModelMetadata(name="test-model", customProperties={"accuracy": 0.99})
    annotations = md.to_annotations_dict()
    assert "name" in annotations
    assert "customProperties+json" in annotations


def test_to_annotations_dict_skips_none_values():
    md = ModelMetadata(name="test-model")
    annotations = md.to_annotations_dict()
    assert "name" in annotations
    assert "description" not in annotations
    assert "author" not in annotations
