#!/usr/bin/env python3
# tests for notification module - integration tests

from datetime import datetime, timedelta

from AppKit import NSAlertFirstButtonReturn, NSAlertSecondButtonReturn

from notification import (
    NotificationResponse,
    ensure_app_initialized,
    create_meeting_alert,
    create_simple_alert,
    bring_to_front,
    parse_alert_response,
    show_meeting_notification,
    show_simple_notification,
)


# ##################################################################
# test ensure app initialized
# proves we can initialize the nsapplication
def test_ensure_app_initialized():
    app = ensure_app_initialized()
    assert app is not None, "Failed to initialize NSApplication"


# ##################################################################
# test ensure app initialized idempotent
# proves calling multiple times is safe
def test_ensure_app_initialized_idempotent():
    app1 = ensure_app_initialized()
    app2 = ensure_app_initialized()
    # should return same instance
    assert app1 is app2


# ##################################################################
# test notification response enum
# proves the enum values are correct
def test_notification_response_enum():
    assert NotificationResponse.JOIN.value == "join"
    assert NotificationResponse.DISMISS.value == "dismiss"
    assert NotificationResponse.CLOSED.value == "closed"


# ##################################################################
# test notification response enum members
# proves all expected enum members exist
def test_notification_response_enum_members():
    members = list(NotificationResponse)
    assert len(members) == 3
    assert NotificationResponse.JOIN in members
    assert NotificationResponse.DISMISS in members
    assert NotificationResponse.CLOSED in members


# ##################################################################
# test create meeting alert
# proves we can create and configure a meeting alert
def test_create_meeting_alert():
    ensure_app_initialized()

    meeting_title = "Test Meeting"
    start_time = datetime.now() + timedelta(minutes=2)
    minutes_until = 2

    alert = create_meeting_alert(meeting_title, start_time, minutes_until)
    assert alert is not None

    # verify alert was configured
    info_text = alert.informativeText()
    assert meeting_title in info_text
    assert "minutes from now" in info_text

    # verify buttons were added
    buttons = alert.buttons()
    assert len(buttons) == 2


# ##################################################################
# test create simple alert
# proves we can create and configure a simple alert
def test_create_simple_alert():
    ensure_app_initialized()

    title = "Test Title"
    message = "Test Message"

    alert = create_simple_alert(title, message)
    assert alert is not None

    # verify alert was configured
    assert title in alert.messageText()
    assert message in alert.informativeText()

    # verify button was added
    buttons = alert.buttons()
    assert len(buttons) == 1


# ##################################################################
# test bring to front
# proves bring_to_front runs without error
def test_bring_to_front():
    ensure_app_initialized()
    # should not raise any exception
    bring_to_front()


# ##################################################################
# test parse alert response join
# proves first button returns join
def test_parse_alert_response_join():
    response = parse_alert_response(NSAlertFirstButtonReturn)
    assert response == NotificationResponse.JOIN


# ##################################################################
# test parse alert response dismiss
# proves second button returns dismiss
def test_parse_alert_response_dismiss():
    response = parse_alert_response(NSAlertSecondButtonReturn)
    assert response == NotificationResponse.DISMISS


# ##################################################################
# test parse alert response closed
# proves other responses return closed
def test_parse_alert_response_closed():
    # any other value should return closed
    response = parse_alert_response(9999)
    assert response == NotificationResponse.CLOSED


# ##################################################################
# test notification functions are callable
# proves the notification functions are properly defined
def test_notification_functions_callable():
    assert callable(show_meeting_notification)
    assert callable(show_simple_notification)


# ##################################################################
# test notification function signatures
# proves the notification functions have correct parameters
def test_notification_function_signatures():
    import inspect

    sig = inspect.signature(show_meeting_notification)
    params = list(sig.parameters.keys())
    assert "meeting_title" in params
    assert "start_time" in params
    assert "minutes_until" in params

    sig2 = inspect.signature(show_simple_notification)
    params2 = list(sig2.parameters.keys())
    assert "title" in params2
    assert "message" in params2
