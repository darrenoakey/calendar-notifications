#!/usr/bin/env python3
# zoom launcher module for opening zoom meetings directly

import subprocess
from typing import Optional

from zoom_parser import ZoomMeeting


# ##################################################################
# launch zoom meeting
# opens a zoom meeting using the zoommtg url scheme
def launch_zoom_meeting(meeting: ZoomMeeting) -> bool:
    return open_zoommtg_url(meeting.zoommtg_url)


# ##################################################################
# open zoommtg url
# opens a zoommtg:// url using macos open command
def open_zoommtg_url(zoommtg_url: str) -> bool:
    if not zoommtg_url.startswith("zoommtg://"):
        return False

    try:
        # use macos open command to launch the url
        # this triggers the zoom app to handle the zoommtg:// scheme
        result = subprocess.run(["open", zoommtg_url], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


# ##################################################################
# check zoom installed
# verifies that zoom is installed on the system
def check_zoom_installed() -> bool:
    try:
        # check if zoom app exists
        result = subprocess.run(
            ["mdfind", "kMDItemCFBundleIdentifier == 'us.zoom.xos'"], capture_output=True, text=True, timeout=10
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


# ##################################################################
# get zoom app path
# returns the path to the zoom application
def get_zoom_app_path() -> Optional[str]:
    try:
        result = subprocess.run(
            ["mdfind", "kMDItemCFBundleIdentifier == 'us.zoom.xos'"], capture_output=True, text=True, timeout=10
        )
        paths = result.stdout.strip().split("\n")
        return paths[0] if paths and paths[0] else None
    except Exception:
        return None
