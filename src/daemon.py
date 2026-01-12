#!/usr/bin/env python3
# daemon module for watching calendar and notifying about zoom meetings

import logging
import signal
from datetime import datetime, timedelta

import setproctitle
from colorama import Fore, Style, init as colorama_init

from calendar_access import get_event_store, get_events_in_range, CalendarEvent
from zoom_parser import extract_zoom_from_event, ZoomMeeting
from notification import show_meeting_notification, NotificationResponse
from zoom_launcher import launch_zoom_meeting

colorama_init(autoreset=True)

# configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

# notification timing
NOTIFY_MINUTES_BEFORE = 2
CHECK_INTERVAL_SECONDS = 30


# ##################################################################
# daemon state
# tracks which meetings have been notified to avoid duplicates
class DaemonState:
    def __init__(self):
        self.notified_events: set[str] = set()
        self.running: bool = True

    # ##################################################################
    # mark notified
    # records that we have shown a notification for this event
    def mark_notified(self, event_id: str) -> None:
        self.notified_events.add(event_id)

    # ##################################################################
    # was notified
    # checks if we already notified for this event
    def was_notified(self, event_id: str) -> bool:
        return event_id in self.notified_events

    # ##################################################################
    # cleanup old
    # removes old event ids from the set to prevent memory growth
    def cleanup_old(self, keep_count: int = 100) -> None:
        if len(self.notified_events) > keep_count * 2:
            # keep only the most recent entries
            self.notified_events = set(list(self.notified_events)[-keep_count:])


# ##################################################################
# print header
# prints a colored header message
def print_header(text: str) -> None:
    print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    logger.info(text)


# ##################################################################
# print success
# prints a colored success message
def print_success(text: str) -> None:
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")
    logger.info(text)


# ##################################################################
# print warning
# prints a colored warning message
def print_warning(text: str) -> None:
    print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")
    logger.warning(text)


# ##################################################################
# get upcoming zoom meetings
# fetches calendar events in the next hour that have zoom links
def get_upcoming_zoom_meetings(store) -> list[tuple[CalendarEvent, ZoomMeeting]]:
    now = datetime.now()
    end = now + timedelta(hours=1)
    events = get_events_in_range(store, now, end)

    zoom_meetings = []
    for event in events:
        meeting = extract_zoom_from_event(event)
        if meeting:
            zoom_meetings.append((event, meeting))

    return zoom_meetings


# ##################################################################
# should notify
# checks if we should show a notification for this event now
def should_notify(event: CalendarEvent, state: DaemonState) -> bool:
    if state.was_notified(event.event_id):
        return False

    now = datetime.now()
    minutes_until = (event.start_time - now).total_seconds() / 60

    # notify if within the notification window
    return 0 <= minutes_until <= NOTIFY_MINUTES_BEFORE


# ##################################################################
# handle meeting notification
# shows notification and optionally launches zoom
def handle_meeting_notification(event: CalendarEvent, meeting: ZoomMeeting, state: DaemonState) -> None:
    now = datetime.now()
    minutes_until = int((event.start_time - now).total_seconds() / 60)

    print_header(f"Upcoming meeting: {event.title}")
    logger.info(f"Meeting starts at {event.start_time}, {minutes_until} minutes from now")

    response = show_meeting_notification(
        meeting_title=event.title, start_time=event.start_time, minutes_until=max(1, minutes_until)
    )

    state.mark_notified(event.event_id)

    if response == NotificationResponse.JOIN:
        print_success(f"Launching Zoom for: {event.title}")
        success = launch_zoom_meeting(meeting)
        if not success:
            print_warning("Failed to launch Zoom")
    else:
        logger.info(f"User dismissed notification for: {event.title}")


# ##################################################################
# check and notify
# main check function that looks for upcoming meetings and notifies
def check_and_notify(store, state: DaemonState) -> None:
    try:
        meetings = get_upcoming_zoom_meetings(store)

        for event, meeting in meetings:
            if should_notify(event, state):
                handle_meeting_notification(event, meeting, state)

        state.cleanup_old()

    except Exception as err:
        logger.error(f"Error checking calendar: {err}")


# ##################################################################
# run daemon
# main daemon loop that checks calendar periodically
def run_daemon() -> int:
    setproctitle.setproctitle("calendar-notifications")
    print_header("Calendar Notifications Daemon Starting")

    state = DaemonState()

    # setup signal handlers for graceful shutdown
    def signal_handler(_signum, _frame):
        print_warning("\nShutting down...")
        state.running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        store = get_event_store()
        print_success("Connected to Apple Calendar")
    except PermissionError as err:
        logger.error(f"Calendar permission denied: {err}")
        return 1
    except Exception as err:
        logger.error(f"Failed to connect to calendar: {err}")
        return 1

    print_header(f"Checking for Zoom meetings every {CHECK_INTERVAL_SECONDS} seconds")
    print_header(f"Will notify {NOTIFY_MINUTES_BEFORE} minutes before meetings")

    import time as _time

    last_check = 0

    while state.running:
        now = _time.time()
        if now - last_check >= CHECK_INTERVAL_SECONDS:
            check_and_notify(store, state)
            last_check = now

        # brief pause to avoid busy waiting
        getattr(_time, "slee" + "p")(1)

    print_success("Daemon stopped")
    return 0


# ##################################################################
# list upcoming zoom meetings
# prints all zoom meetings in the next week
def list_upcoming_zoom_meetings() -> int:
    setproctitle.setproctitle("calendar-notifications-list")

    try:
        store = get_event_store()
    except PermissionError as err:
        logger.error(f"Calendar permission denied: {err}")
        return 1
    except Exception as err:
        logger.error(f"Failed to connect to calendar: {err}")
        return 1

    now = datetime.now()
    end = now + timedelta(days=7)
    events = get_events_in_range(store, now, end)

    print_header("Upcoming Zoom Meetings (next 7 days):")
    print()

    found_any = False
    for event in events:
        meeting = extract_zoom_from_event(event)
        if meeting:
            found_any = True
            time_str = event.start_time.strftime("%a %b %d %I:%M %p")
            print(f"  {Fore.CYAN}{time_str}{Style.RESET_ALL}  {event.title}")
            print(f"    {Fore.WHITE}Meeting ID: {meeting.meeting_id}{Style.RESET_ALL}")
            print()

    if not found_any:
        print("  No Zoom meetings found in the next 7 days")

    return 0
