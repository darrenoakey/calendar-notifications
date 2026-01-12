#!/usr/bin/env python3
# pytest configuration for calendar-notifications tests


# ##################################################################
# pytest addoption
# adds custom command line options for test configuration
def pytest_addoption(parser):
    parser.addoption(
        "--runvisual", action="store_true", default=False, help="run visual tests that require user interaction"
    )


# ##################################################################
# pytest configure
# registers custom markers
def pytest_configure(config):
    config.addinivalue_line("markers", "visual: mark test as visual (requires user interaction)")
