import json
import subprocess
import tempfile
import typing as t
from hashlib import sha256
from pathlib import Path

import pytest

from omlmd.constants import MIME_APPLICATION_MLMODEL
from omlmd.helpers import Helper
from omlmd.listener import Event, Listener
from omlmd.model_metadata import ModelMetadata, deserialize_mdfile
from omlmd.provider import OMLMDRegistry


def test_call_push_using_md_from_file(mocker):
    helper = Helper()
    mocker.patch.object(helper, "push", return_value=None)

    md = {
        "name": "mnist",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": 0.987,
    }
    with tempfile.NamedTemporaryFile(delete=True, mode="w") as f:
        f.write(json.dumps(md))
        f.flush()
        md = deserialize_mdfile(f.name)

    helper.push("localhost:8080/mmortari/ml-iris:v1", "some-file", **md)
    helper.push.assert_called_once_with(
        "localhost:8080/mmortari/ml-iris:v1",
        "some-file",
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        accuracy=0.987,
    )


def test_push_event(mocker):
    registry = OMLMDRegistry()
    m = mocker.MagicMock()
    m.headers = {"Docker-Content-Digest": "sha256:123"}
    mocker.patch.object(
        registry,
        "push",
        return_value=m,
    )
    omlmd = Helper(registry)

    events = []

    class MyListener(Listener):
        def update(self, source: t.Any, event: Event) -> None:
            events.append(event)

    omlmd.add_listener(MyListener())

    md = {
        "name": "mnist",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": 0.987,
    }
    omlmd.push("unexistent:8080/testorgns/ml-iris:v1", "README.md", **md)

    assert len(events) == 1
    e0 = events[0]
    assert e0.target == "unexistent:8080/testorgns/ml-iris:v1"
    assert e0.metadata == ModelMetadata.from_dict(md)


@pytest.mark.e2e
def test_push_pull_chunked(tmp_path, target):
    omlmd = Helper()

    md = {
        "name": "mnist",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": 0.987,
    }
    here = Path.cwd()
    temp = here / "temp"
    base_size = 16 * 1024 * 1024 * 3  # 48MB
    try:
        subprocess.run(
            [
                "dd",
                "if=/dev/null",
                f"of={temp}",
                "bs=1",
                "count=0",
                f"seek={base_size}",
            ],
        )

        omlmd.push(target, temp, **md)
        omlmd.pull(target, tmp_path)
        assert len(list(tmp_path.iterdir())) == 3
        assert tmp_path.joinpath(temp.name).stat().st_size == base_size
    finally:
        temp.unlink()


@pytest.mark.e2e
def test_e2e_push_pull(tmp_path, target):
    omlmd = Helper()
    omlmd.push(
        target,
        Path(__file__).parent / ".." / "README.md",
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        accuracy=0.987,
    )
    omlmd.pull(target, tmp_path)
    assert len(list(tmp_path.iterdir())) == 3


@pytest.mark.e2e
def test_e2e_push_pull_with_filters(tmp_path, target):
    omlmd = Helper()
    omlmd.push(
        target,
        Path(__file__).parent / ".." / "README.md",
        name="mnist",
        description="Lorem ipsum",
        author="John Doe",
        accuracy=0.987,
    )
    omlmd.pull(target, tmp_path, media_types=[MIME_APPLICATION_MLMODEL])
    assert len(list(tmp_path.iterdir())) == 1


@pytest.mark.e2e
def test_e2e_push_pull_column(tmp_path, target):
    omlmd = Helper()
    md = {
        "name": "using : in the filename",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": 0.987,
    }
    content = "Hello, World!"
    content_sha = sha256(content.encode("utf-8")).hexdigest()
    here = Path.cwd()
    temp = here / ("sha256:" + content_sha)
    try:
        with open(temp, "w") as f:
            f.write(content)

        omlmd.push(target, temp, **md)
        omlmd.pull(target, tmp_path)
        with open(tmp_path.joinpath(temp.name), "r") as f:
            pulled = f.read()
            assert pulled == content
            pulled_sha = sha256(pulled.encode("utf-8")).hexdigest()
            assert pulled_sha == content_sha
    finally:
        temp.unlink()
