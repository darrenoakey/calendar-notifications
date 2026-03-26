![](banner.jpg)

# Calendar Notifications

A macOS menu bar daemon that monitors your calendar and provides notifications for upcoming Zoom meetings, with one-click launch capability.

## Purpose

This tool runs in the background on macOS, watching your calendar for Zoom meetings. When a meeting is approaching, it displays a notification that lets you join the Zoom call directly with a single click.

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Start the Daemon

Run the notification daemon in the foreground:

```bash
./run start
```

The daemon will continuously monitor your calendar and send notifications before Zoom meetings.

### List Upcoming Zoom Meetings

View all upcoming Zoom meetings in the next week:

```bash
./run list
```

Or use the alias:

```bash
./run show
```

### Test Zoom Launch

Find the next Zoom meeting and attempt to launch it (useful for testing):

```bash
./run test-zoom
```

### Run Tests

Run a specific test:

```bash
./run test src/calendar_access_test.py::test_get_event_store
```

### Run Linter

Check code quality:

```bash
./run lint
```

### Run Full Quality Checks

Run the complete test suite and quality gates:

```bash
./run check
```

## Examples

**Starting the daemon:**
```bash
$ ./run start
Calendar notification daemon started...
Monitoring for upcoming Zoom meetings...
```

**Listing meetings:**
```bash
$ ./run list
Upcoming Zoom meetings:
  Mon Jan 13 10:00 AM - Team Standup
  Mon Jan 13 2:00 PM - Project Review
  Tue Jan 14 11:00 AM - 1:1 with Manager
```

**Testing Zoom launch:**
```bash
$ ./run test-zoom
Finding next Zoom meeting...
Found: Team Standup
  Start: Mon Jan 13 10:00 AM
  Meeting ID: 123456789
  Original URL: https://zoom.us/j/123456789
  ZoomMTG URL: zoommtg://zoom.us/join?confno=123456789
Launching Zoom...
Zoom launched successfully
```

## Requirements

- macOS (uses native Calendar and notification APIs)
- Python 3.x
- Zoom desktop application installed
- Calendar access permission granted to Terminal/your IDE

## License

This project is licensed under [CC BY-NC 4.0](https://darren-static.waft.dev) - free to use and modify, but no commercial use without permission.
