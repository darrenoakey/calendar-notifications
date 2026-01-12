#!/usr/bin/env python3
# tests for zoom_launcher module - real integration tests

from zoom_launcher import (
    check_zoom_installed,
    get_zoom_app_path,
    open_zoommtg_url,
)


# ##################################################################
# test check zoom installed
# proves we can detect if zoom is installed on the system
def test_check_zoom_installed():
    is_installed = check_zoom_installed()
    print(f"\nZoom installed: {is_installed}")
    # we expect zoom to be installed for this to be useful
    assert is_installed, "Zoom is not installed on this system"


# ##################################################################
# test get zoom app path
# proves we can find the zoom application path
def test_get_zoom_app_path():
    path = get_zoom_app_path()
    print(f"\nZoom app path: {path}")
    assert path is not None, "Could not find Zoom app path"
    assert "zoom" in path.lower(), "Path does not appear to be Zoom"


# ##################################################################
# test open zoommtg url validation
# proves we validate zoommtg urls correctly
def test_open_zoommtg_url_validation():
    # should reject non-zoommtg urls
    assert not open_zoommtg_url("https://zoom.us/j/123")
    assert not open_zoommtg_url("invalid://url")
    assert not open_zoommtg_url("")
