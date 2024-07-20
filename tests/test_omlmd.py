from omlmd.model_metadata import ModelMetadata

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
