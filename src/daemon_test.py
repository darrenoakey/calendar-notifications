#!/usr/bin/env python3
# tests for daemon module - integration tests

from datetime import datetime, timedelta
import io
import sys

from calendar_access import CalendarEvent
from daemon import (
    DaemonState,
    get_upcoming_zoom_meetings,
    should_notify,
    get_event_store,
    print_header,
    print_success,
    print_warning,
    check_and_notify,
    list_upcoming_zoom_meetings,
)


# ##################################################################
# test daemon state
# proves the state tracking works correctly
def test_daemon_state():
    state = DaemonState()

    # initially nothing is notified
    assert not state.was_notified("event1")

    # mark as notified
    state.mark_notified("event1")
    assert state.was_notified("event1")
    assert not state.was_notified("event2")

    # cleanup should work
    for i in range(300):
        state.mark_notified(f"event_{i}")
    state.cleanup_old(keep_count=100)
    assert len(state.notified_events) <= 200


# ##################################################################
# test daemon state running flag
# proves the running flag works correctly
def test_daemon_state_running():
    state = DaemonState()
    assert state.running is True
    state.running = False
    assert state.running is False


# ##################################################################
# test should notify
# proves the notification timing logic works
def test_should_notify():
    state = DaemonState()

    # event starting in 1 minute - should notify
    event_soon = CalendarEvent(
        title="Soon Meeting",
        start_time=datetime.now() + timedelta(minutes=1),
        end_time=datetime.now() + timedelta(minutes=31),
        notes=None,
        url=None,
        location=None,
        calendar_name="Test",
        event_id="event_soon",
    )
    assert should_notify(event_soon, state)

    # mark as notified - should not notify again
    state.mark_notified("event_soon")
    assert not should_notify(event_soon, state)

    # event starting in 30 minutes - should not notify yet
    event_later = CalendarEvent(
        title="Later Meeting",
        start_time=datetime.now() + timedelta(minutes=30),
        end_time=datetime.now() + timedelta(minutes=60),
        notes=None,
        url=None,
        location=None,
        calendar_name="Test",
        event_id="event_later",
    )
    assert not should_notify(event_later, state)

    # event already started - should not notify
    event_past = CalendarEvent(
        title="Past Meeting",
        start_time=datetime.now() - timedelta(minutes=5),
        end_time=datetime.now() + timedelta(minutes=25),
        notes=None,
        url=None,
        location=None,
        calendar_name="Test",
        event_id="event_past",
    )
    assert not should_notify(event_past, state)


# ##################################################################
# test get upcoming zoom meetings
# proves we can find zoom meetings in the calendar
def test_get_upcoming_zoom_meetings():
    store = get_event_store()
    meetings = get_upcoming_zoom_meetings(store)

    print(f"\nFound {len(meetings)} Zoom meetings in next hour:")
    for event, meeting in meetings:
        print(f"  - {event.start_time.strftime('%H:%M')} | {event.title}")
        print(f"    ID: {meeting.meeting_id}")

    # this is an informational test - may or may not have meetings in next hour
    assert isinstance(meetings, list)


# ##################################################################
# test print header
# proves print_header outputs correctly
def test_print_header():
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    print_header("Test Header")
    sys.stdout = old_stdout
    output = captured.getvalue()
    assert "Test Header" in output


# ##################################################################
# test print success
# proves print_success outputs correctly
def test_print_success():
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    print_success("Test Success")
    sys.stdout = old_stdout
    output = captured.getvalue()
    assert "Test Success" in output


# ##################################################################
# test print warning
# proves print_warning outputs correctly
def test_print_warning():
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    print_warning("Test Warning")
    sys.stdout = old_stdout
    output = captured.getvalue()
    assert "Test Warning" in output


# ##################################################################
# test check and notify
# proves check_and_notify runs without error
def test_check_and_notify():
    store = get_event_store()
    state = DaemonState()
    # mark all current events as already notified to prevent popups
    meetings = get_upcoming_zoom_meetings(store)
    for event, _ in meetings:
        state.mark_notified(event.event_id)
    # should run without error
    check_and_notify(store, state)


# ##################################################################
# test list upcoming zoom meetings
# proves list_upcoming_zoom_meetings runs and returns 0
def test_list_upcoming_zoom_meetings():
    result = list_upcoming_zoom_meetings()
    assert result == 0
