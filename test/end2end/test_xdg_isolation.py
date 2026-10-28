"""The XDG isolation fixture must not replace the cached XDG paths.

CI presets ``XDG_DATA_HOME`` and restores ``$XDG_DATA_HOME/mycroft/intent_cache*``
between runs, so a serial run must keep the paths it was given.
"""
import os

import pytest

from conftest import XDG_VARS

# Imported before the session fixture runs, so this is the pre-fixture state.
BEFORE = {var: os.environ.get(var) for var in XDG_VARS}


@pytest.mark.skipif(os.environ.get("PYTEST_XDIST_WORKER") is not None,
                    reason="xdist workers get a private XDG tree on purpose")
def test_serial_run_keeps_the_xdg_paths_it_was_given():
    assert {var: os.environ.get(var) for var in XDG_VARS} == BEFORE
