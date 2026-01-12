#!/usr/bin/env python3
# notification module for macos popup dialogs

from enum import Enum
from datetime import datetime

from AppKit import (
    NSAlert,
    NSAlertFirstButtonReturn,
    NSAlertSecondButtonReturn,
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSRunningApplication,
    NSApplicationActivateIgnoringOtherApps,
)


class NotificationResponse(Enum):
    # user response options for the notification dialog
    JOIN = "join"
    DISMISS = "dismiss"
    CLOSED = "closed"


# ##################################################################
# ensure app initialized
# makes sure nsapplication is running so we can show alerts
def ensure_app_initialized():
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    return app


# ##################################################################
# create meeting alert
# creates and configures an nsalert for a meeting notification
def create_meeting_alert(meeting_title: str, start_time: datetime, minutes_until: int) -> NSAlert:
    alert = NSAlert.alloc().init()
    alert.setMessageText_("Upcoming Zoom Meeting")
    alert.setInformativeText_(
        f"{meeting_title}\n\n" f"Starts at {start_time.strftime('%I:%M %p')}\n" f"({minutes_until} minutes from now)"
    )
    alert.addButtonWithTitle_("Join Zoom")
    alert.addButtonWithTitle_("Dismiss")
    return alert


# ##################################################################
# create simple alert
# creates and configures an nsalert for a simple notification
def create_simple_alert(title: str, message: str) -> NSAlert:
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(message)
    alert.addButtonWithTitle_("OK")
    return alert


# ##################################################################
# bring to front
# activates the current application to bring alert to front
def bring_to_front() -> None:
    NSRunningApplication.currentApplication().activateWithOptions_(NSApplicationActivateIgnoringOtherApps)


# ##################################################################
# parse alert response
# converts nsalert response code to notificationresponse enum
def parse_alert_response(response: int) -> NotificationResponse:
    if response == NSAlertFirstButtonReturn:
        return NotificationResponse.JOIN
    elif response == NSAlertSecondButtonReturn:
        return NotificationResponse.DISMISS
    else:
        return NotificationResponse.CLOSED


# ##################################################################
# show meeting notification
# displays a modal alert for an upcoming zoom meeting
def show_meeting_notification(meeting_title: str, start_time: datetime, minutes_until: int = 2) -> NotificationResponse:
    ensure_app_initialized()
    alert = create_meeting_alert(meeting_title, start_time, minutes_until)
    bring_to_front()
    response = alert.runModal()
    return parse_alert_response(response)


# ##################################################################
# show simple notification
# displays a simple info alert with just an ok button
def show_simple_notification(title: str, message: str) -> None:
    ensure_app_initialized()
    alert = create_simple_alert(title, message)
    bring_to_front()
    alert.runModal()
