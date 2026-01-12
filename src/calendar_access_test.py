#!/usr/bin/env python3
# tests for calendar_access module - real integration tests against apple calendar

from datetime import datetime

from calendar_access import get_event_store, get_events_next_week, get_upcoming_events, CalendarEvent


# ##################################################################
# test get event store
# proves we can connect to apple calendar and get permission
def test_get_event_store():
    store = get_event_store()
    assert store is not None, "Failed to get event store"


# ##################################################################
# test get events next week
# proves we can retrieve calendar events for the next 7 days
def test_get_events_next_week():
    events = get_events_next_week()
    # we expect at least some events in the calendar
    assert isinstance(events, list), "Expected list of events"
    print(f"\nFound {len(events)} events in the next week:")
    for event in events:
        print(f"  - {event.start_time.strftime('%Y-%m-%d %H:%M')} | {event.title}")
        if event.notes:
            print(f"    Notes: {event.notes[:100]}...")
        if event.url:
            print(f"    URL: {event.url}")
        if event.location:
            print(f"    Location: {event.location}")


# ##################################################################
# test event structure
# proves that events have the expected structure and types
def test_event_structure():
    events = get_upcoming_events(days=7)
    # require at least one event to test structure
    assert len(events) > 0, "No events in calendar to test structure"

    event = events[0]
    assert isinstance(event, CalendarEvent)
    assert isinstance(event.title, str)
    assert isinstance(event.start_time, datetime)
    assert isinstance(event.end_time, datetime)
    assert isinstance(event.event_id, str)
    assert isinstance(event.calendar_name, str)


# ##################################################################
# test find zoom events
# proves we can find events that contain zoom links
def test_find_zoom_events():
    events = get_events_next_week()
    zoom_events = []

    for event in events:
        has_zoom = False
        zoom_source = None

        # check notes for zoom link
        if event.notes and "zoom" in event.notes.lower():
            has_zoom = True
            zoom_source = "notes"

        # check url for zoom link
        if event.url and "zoom" in event.url.lower():
            has_zoom = True
            zoom_source = "url"

        # check location for zoom link
        if event.location and "zoom" in event.location.lower():
            has_zoom = True
            zoom_source = "location"

        if has_zoom:
            zoom_events.append((event, zoom_source))

    print(f"\nFound {len(zoom_events)} events with Zoom links:")
    for event, source in zoom_events:
        print(f"  - {event.start_time.strftime('%Y-%m-%d %H:%M')} | {event.title}")
        print(f"    Zoom found in: {source}")

    # user confirmed they have zoom meetings, so we expect at least one
    assert len(zoom_events) > 0, "Expected at least one Zoom event in calendar"
