from omlmd.helpers import Helper
from omlmd.listener import Event, Listener, PushEvent
from omlmd.model_metadata import ModelMetadata, deserialize_mdfile
import tempfile
import json
from omlmd.provider import OMLMDRegistry
import pytest
from pathlib import Path
from model_registry import ModelRegistry
from urllib.parse import quote
from omlmd.helpers import download_file


def from_oci_to_kfmr(model_registry: ModelRegistry, push_event: PushEvent, sha: str) -> None:
    rm = model_registry.register_model(
        name=push_event.metadata.name,
        uri=f"oci-artifact://{push_event.target}",
        version=quote(sha),
        author=push_event.metadata.author,
        description=push_event.metadata.description,
        model_format_name=push_event.metadata.model_format_name,
        model_format_version=push_event.metadata.model_format_version,
        metadata=push_event.metadata.customProperties,
    )
    return rm


@pytest.mark.e2e_model_registry
def test_e2e_model_registry_scenario1(tmp_path, target):
    """
    Given a ML model and some metadata, to OCI registry, and then to KF Model Registry (at once)
    """
    model_registry = ModelRegistry("http://localhost", 8081, author="mmortari", is_secure=False)

    class ListenerForModelRegistry(Listener):
        sha = None
        rm = None 

        def update(self, source: Helper, event: Event) -> None:
            if isinstance(event, PushEvent):
                self.sha = source.registry.get_manifest_response(event.target).headers["Docker-Content-Digest"]
                print(self.sha)
                self.rm = from_oci_to_kfmr(model_registry, event, self.sha)
    
    listener = ListenerForModelRegistry()
    omlmd = Helper()
    omlmd.add_listener(listener)
    
    # assuming a model ...
    model_file = Path(__file__).parent / ".." / "README.md"
    # ...with some additional characteristics
    accuracy_value = 0.987

    omlmd.push(
        target,
        model_file,
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        accuracy=accuracy_value
    )

    v = quote(listener.sha)

    rm = model_registry.get_registered_model("mnist")
    assert rm.id == listener.rm.id
    assert rm.name == "mnist"

    mv = model_registry.get_model_version("mnist", v)
    assert mv.description == "Lorem ipsum"
    assert mv.author == "John Doe"
    assert mv.custom_properties == {'accuracy': 0.987}

    ma = model_registry.get_model_artifact("mnist", v)
    assert ma.uri == f"oci-artifact://{target}"

    # curl http://localhost:5001/v2/testorgns/ml-model-artifact/manifests/v1 -H "Accept: application/vnd.oci.image.manifest.v1+json" --verbose
    # or replace tag with target's as needed.


@pytest.mark.e2e_model_registry
def test_e2e_model_registry_scenario2(tmp_path, target):
    """
    Given some metadata entry in KF model registry, attempt retrieve pointed ML model file asset, then OCI registry
    """
    model_registry = ModelRegistry("http://localhost", 8081, author="mmortari", is_secure=False)

    # assuming a model indexed on KF Model Registry ...
    registeredmodel_name = "mnist"
    version_name = "v0.1"
    rm = model_registry.register_model(
        registeredmodel_name,
        "https://github.com/tarilabs/demo20231212/raw/main/v1.nb20231206162408/mnist.onnx",
        model_format_name="onnx",
        model_format_version="1",
        version=version_name,
        description="lorem ipsum mnist",
        metadata={
            "accuracy": 3.14,
            "license": "apache-2.0",
        }
    )

    lookup_name = "mnist"
    lookup_version = "v0.1" 

    registered_model = model_registry.get_registered_model(lookup_name)
    model_version = model_registry.get_model_version(lookup_name, lookup_version)
    model_artifact = model_registry.get_model_artifact(lookup_name, lookup_version)

    file_from_mr = download_file(model_artifact.uri)

    oci_reference = f"localhost:5001/testorgns/{lookup_name}:{lookup_version}"
    # ideally, the oci reference should include the registeredmodel name (above), but for e2e testing we're going to use the designated reference
    oci_reference = f"localhost:5001/testorgns/ml-model-artifact:{lookup_version}"

    omlmd = Helper()
    omlmd.push(
        oci_reference,
        file_from_mr,
        name=lookup_name,
        description=model_version.description,
        author=model_version.author,
        model_format_name=model_artifact.model_format_name,
        model_format_version=model_artifact.model_format_version,
        **model_version.custom_properties
    )
    # curl http://localhost:5001/v2/testorgns/ml-model-artifact/manifests/v0.1 -H "Accept: application/vnd.oci.image.manifest.v1+json" --verbose
    # tag v0.1 is defined in this test scenario.
