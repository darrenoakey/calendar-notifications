#!/usr/bin/env python3
# tests for conftest module - validates pytest configuration

from conftest import pytest_addoption, pytest_configure


# ##################################################################
# test pytest addoption
# proves the addoption function exists and is callable
def test_pytest_addoption():
    # create a minimal parser substitute that just records calls
    class RecordingParser:
        def __init__(self):
            self.options = []

        def addoption(self, *args, **kwargs):
            self.options.append((args, kwargs))

    parser = RecordingParser()
    pytest_addoption(parser)
    assert len(parser.options) == 1
    assert "--runvisual" in parser.options[0][0]


# ##################################################################
# test pytest configure
# proves the configure function exists and is callable
def test_pytest_configure():
    class RecordingConfig:
        def __init__(self):
            self.lines = []

        def addinivalue_line(self, key, value):
            self.lines.append((key, value))

    config = RecordingConfig()
    pytest_configure(config)
    assert len(config.lines) == 1
    assert config.lines[0][0] == "markers"
    assert "visual" in config.lines[0][1]
