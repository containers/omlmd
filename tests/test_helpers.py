from omlmd.helpers import Helper
from omlmd.model_metadata import deserialize_mdfile
import tempfile
import json

def test_call_push_using_md_from_file(mocker):
    helper = Helper()
    mocker.patch.object(helper, "push", return_value=None)

    md = {
        "name": "mnist",
        "description": "Lorem ipsum",
        "author": "John Doe",
        "accuracy": .987
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
        accuracy=0.987
    )
