import os

# config.py reads POSTGRES_*/OPENAI_API_KEY eagerly at import time (module-
# level `settings = _load_settings()`), and bootstrap.new_use_case imports
# it transitively — same issue lexi-rag-ms's own CI works around with dummy
# values for pytest, since these tests never open a real connection or call
# OpenAI (they hand handle() a fake-backed use case instead).
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import importlib.util
import pathlib


def load_sibling_main(test_file: str):
    """Loads the main.py next to a given test file as a uniquely-named
    module — see the same helper in cloud-native/lexi-card-srl/conftest.py for why
    a plain `import main` isn't safe once there's more than one endpoint."""
    directory = pathlib.Path(test_file).parent
    module_name = f"_lambda_main_{directory.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, directory / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
