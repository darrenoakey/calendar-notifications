#!/usr/bin/env python3
# zoom parser module for extracting zoom meeting links from calendar events

import re
from dataclasses import dataclass
from typing import Optional

from calendar_access import CalendarEvent


@dataclass
class ZoomMeeting:
    # represents a parsed zoom meeting with its connection details
    meeting_id: str
    password: Optional[str]
    original_url: str
    zoommtg_url: str


# zoom url patterns to match
ZOOM_PATTERNS = [
    # https://zoom.us/j/MEETING_ID
    r"https?://(?:[\w-]+\.)?zoom\.us/j/(\d+)(?:\?pwd=([a-zA-Z0-9]+))?",
    # https://zoom.us/my/PERSONAL_LINK
    r"https?://(?:[\w-]+\.)?zoom\.us/my/([\w.-]+)",
    # zoommtg://zoom.us/join?confno=MEETING_ID
    r"zoommtg://(?:[\w-]+\.)?zoom\.us/join\?(?:.*&)?confno=(\d+)",
]


# ##################################################################
# find zoom url in text
# searches text for any zoom meeting url pattern
def find_zoom_url_in_text(text: str) -> Optional[str]:
    if not text:
        return None

    for pattern in ZOOM_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


# ##################################################################
# extract zoom from event
# searches all fields of a calendar event for zoom meeting links
def extract_zoom_from_event(event: CalendarEvent) -> Optional[ZoomMeeting]:
    zoom_url = None

    # check url field first (most reliable)
    if event.url:
        zoom_url = find_zoom_url_in_text(event.url)

    # check location field
    if not zoom_url and event.location:
        zoom_url = find_zoom_url_in_text(event.location)

    # check notes field
    if not zoom_url and event.notes:
        zoom_url = find_zoom_url_in_text(event.notes)

    if not zoom_url:
        return None

    return parse_zoom_url(zoom_url)


# ##################################################################
# parse zoom url
# parses a zoom url and extracts meeting id and password
def parse_zoom_url(url: str) -> Optional[ZoomMeeting]:
    if not url:
        return None

    meeting_id = None
    password = None

    # try to extract meeting id and password
    # pattern: https://zoom.us/j/MEETING_ID?pwd=PASSWORD
    match = re.search(r"zoom\.us/j/(\d+)", url, re.IGNORECASE)
    if match:
        meeting_id = match.group(1)

    # try personal meeting room format
    if not meeting_id:
        match = re.search(r"zoom\.us/my/([\w.-]+)", url, re.IGNORECASE)
        if match:
            # personal links don't have numeric meeting ids
            # we use the personal link as the id
            meeting_id = match.group(1)

    # try zoommtg format
    if not meeting_id:
        match = re.search(r"confno=(\d+)", url, re.IGNORECASE)
        if match:
            meeting_id = match.group(1)

    if not meeting_id:
        return None

    # extract password if present
    pwd_match = re.search(r"[?&]pwd=([a-zA-Z0-9]+)", url)
    if pwd_match:
        password = pwd_match.group(1)

    # build zoommtg url for direct launch
    zoommtg_url = build_zoommtg_url(meeting_id, password)

    return ZoomMeeting(meeting_id=meeting_id, password=password, original_url=url, zoommtg_url=zoommtg_url)


# ##################################################################
# build zoommtg url
# constructs a zoommtg:// url for direct zoom launch
def build_zoommtg_url(meeting_id: str, password: Optional[str] = None) -> str:
    # check if it's a personal room link (non-numeric)
    if not meeting_id.isdigit():
        # personal room links need different handling
        base = f"zoommtg://zoom.us/join?action=join&confno={meeting_id}"
    else:
        base = f"zoommtg://zoom.us/join?action=join&confno={meeting_id}"

    if password:
        base += f"&pwd={password}"

    return base
