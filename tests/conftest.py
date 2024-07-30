import pytest


def pytest_collection_modifyitems(config, items):
    if config.getoption("--e2e"):
        skip_not_e2e = pytest.mark.skip(reason="skipping non-e2e tests")
        for item in items:
            if "e2e" not in item.keywords:
                item.add_marker(skip_not_e2e)
        return
    skip_e2e = pytest.mark.skip(reason="test requires --e2e option to run")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


def pytest_addoption(parser):
    parser.addoption(
        "--e2e", action="store_true", default=False, help="opt-in to run tests marked with e2e"
    )


@pytest.fixture
def target() -> str:
    return "localhost:5001/mmortari/mlartifact:v1"

