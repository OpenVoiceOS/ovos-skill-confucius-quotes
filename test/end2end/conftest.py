"""Per-worker XDG isolation for the ovoscope e2e suite.

Under ``pytest-xdist`` every worker boots its own MiniCroft, and they otherwise
share the default XDG paths — racing to create the same Padatious cache /
identity directories and intermittently raising ``FileExistsError``. Give each
worker its own private XDG tree so those writes never collide.

A serial run has nobody to race, so it keeps the XDG paths it was given. CI
presets ``XDG_DATA_HOME`` and caches ``$XDG_DATA_HOME/mycroft/intent_cache*``
between runs; replacing the variable would send the Padatious cache to a
directory the cache step cannot address, and every run would compile every
intent with FANN from cold. ``XDG_CACHE_HOME`` holds the HuggingFace hub cache
when ``HF_HOME`` is unset, so replacing it re-downloads the m2v model.
"""
import os

import pytest

XDG_VARS = ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
            "XDG_STATE_HOME")


@pytest.fixture(scope="session", autouse=True)
def _isolate_xdg(tmp_path_factory):
    worker = os.environ.get("PYTEST_XDIST_WORKER")
    if worker is None:
        yield
        return
    root = tmp_path_factory.mktemp(f"xdg-{worker}")
    for var in XDG_VARS:
        path = root / var.lower()
        path.mkdir(parents=True, exist_ok=True)
        os.environ[var] = str(path)
    yield
