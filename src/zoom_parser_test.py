#!/usr/bin/env python3
# tests for zoom_parser module - real integration tests against calendar data

from calendar_access import get_events_next_week
from zoom_parser import (
    find_zoom_url_in_text,
    extract_zoom_from_event,
    parse_zoom_url,
    build_zoommtg_url,
    ZoomMeeting,
)


# ##################################################################
# test find zoom url patterns
# proves we can find zoom urls in various text formats
def test_find_zoom_url_patterns():
    # standard zoom link
    text1 = "Join the meeting at https://zoom.us/j/1234567890"
    url1 = find_zoom_url_in_text(text1)
    assert url1 == "https://zoom.us/j/1234567890"

    # zoom link with password
    text2 = "Link: https://zoom.us/j/1234567890?pwd=abc123xyz"
    url2 = find_zoom_url_in_text(text2)
    assert url2 == "https://zoom.us/j/1234567890?pwd=abc123xyz"

    # company subdomain
    text3 = "Meeting: https://company.zoom.us/j/9876543210"
    url3 = find_zoom_url_in_text(text3)
    assert url3 == "https://company.zoom.us/j/9876543210"

    # personal meeting room
    text4 = "My room: https://zoom.us/my/john.smith"
    url4 = find_zoom_url_in_text(text4)
    assert url4 == "https://zoom.us/my/john.smith"


# ##################################################################
# test parse zoom url
# proves we can extract meeting id and password from zoom urls
def test_parse_zoom_url():
    # standard link
    meeting1 = parse_zoom_url("https://zoom.us/j/1234567890")
    assert meeting1 is not None
    assert meeting1.meeting_id == "1234567890"
    assert meeting1.password is None

    # link with password
    meeting2 = parse_zoom_url("https://zoom.us/j/1234567890?pwd=abc123")
    assert meeting2 is not None
    assert meeting2.meeting_id == "1234567890"
    assert meeting2.password == "abc123"


# ##################################################################
# test build zoommtg url
# proves we can build valid zoommtg urls for direct launch
def test_build_zoommtg_url():
    # without password
    url1 = build_zoommtg_url("1234567890")
    assert url1 == "zoommtg://zoom.us/join?action=join&confno=1234567890"

    # with password
    url2 = build_zoommtg_url("1234567890", "abc123")
    assert url2 == "zoommtg://zoom.us/join?action=join&confno=1234567890&pwd=abc123"


# ##################################################################
# test extract zoom from real events
# proves we can find and parse zoom links from actual calendar events
def test_extract_zoom_from_real_events():
    events = get_events_next_week()
    zoom_meetings = []

    for event in events:
        meeting = extract_zoom_from_event(event)
        if meeting:
            zoom_meetings.append((event, meeting))

    print(f"\nFound {len(zoom_meetings)} Zoom meetings in calendar:")
    for event, meeting in zoom_meetings:
        print(f"  - {event.start_time.strftime('%Y-%m-%d %H:%M')} | {event.title}")
        print(f"    Meeting ID: {meeting.meeting_id}")
        print(f"    Original URL: {meeting.original_url}")
        print(f"    ZoomMTG URL: {meeting.zoommtg_url}")

    # user confirmed they have zoom meetings
    assert len(zoom_meetings) > 0, "Expected at least one Zoom meeting in calendar"

    # verify meeting structure
    for event, meeting in zoom_meetings:
        assert isinstance(meeting, ZoomMeeting)
        assert meeting.meeting_id is not None
        assert meeting.zoommtg_url.startswith("zoommtg://")
