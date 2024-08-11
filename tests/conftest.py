import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        skip_e2e = pytest.mark.skip(reason="this is an end-to-end test, requires explicit opt-in --e2e option to run.")
        skip_e2e_model_registry = pytest.mark.skip(reason="this is an end-to-end test, requires explicit opt-in --e2e-model-registry option to run.")
        skip_not_e2e = pytest.mark.skip(reason="skipping non-e2e tests; opt-out of --e2e -like options to run.")
        if "e2e" in item.keywords:
            if not config.getoption("--e2e"):
                item.add_marker(skip_e2e)
            continue
        elif "e2e_model_registry" in item.keywords:
            if not config.getoption("--e2e-model-registry"):
                item.add_marker(skip_e2e_model_registry)
            continue
        
        if config.getoption("--e2e") or config.getoption("--e2e-model-registry"):
            item.add_marker(skip_not_e2e)


def pytest_addoption(parser):
    parser.addoption(
        "--e2e", action="store_true", default=False, help="opt-in to run tests marked with e2e"
    )
    parser.addoption(
        "--e2e-model-registry", action="store_true", default=False, help="opt-in to run tests marked with e2e_model_registry"
    )


@pytest.fixture
def target() -> str:
    return "localhost:5001/testorgns/ml-model-artifact:v1"

