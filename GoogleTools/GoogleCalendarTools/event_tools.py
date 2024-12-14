from datetime import datetime, timedelta
from typing import Optional
from googleapiclient.errors import HttpError
from .calendar_service import get_calendar_service

from langchain_core.tools import tool

@tool
def list_calendars():
    """
    List all available calendars in the Google Calendar account.

    Returns:
        str: Formatted list of available calendars
    """
    try:
        service = get_calendar_service()
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])

        if not calendars:
            return "No calendars found."

        # Format calendars into a readable string
        calendar_list = "\n".join([
            f"- {calendar['summary']} (ID: {calendar['id']})"
            for calendar in calendars
        ])

        return f"Available Calendars:\n{calendar_list}"

    except HttpError as error:
        return f"An error occurred while listing calendars: {error}"

@tool
def list_upcoming_events(calendar_id: Optional[str] = None, max_results: int = 10, days_ahead: int = 30):
    """
    List upcoming events for a specific or primary calendar.

    Args:
        calendar_id (Optional[str]): ID of the calendar to list events from (default: primary)
        max_results (int): Maximum number of events to retrieve (default 10)
        days_ahead (int): Number of days to look ahead for events (default 30)

    Returns:
        str: Formatted list of upcoming events
    """
    try:
        service = get_calendar_service()

        # Use primary calendar if no ID is provided
        if not calendar_id:
            calendar_id = 'primary'

        # Calculate time range
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

        # Retrieve events
        events_result = service.events().list(
            calendarId=calendar_id, 
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return f"No upcoming events found in the next {days_ahead} days."

        # Format event details
        event_details = []
        for i, event in enumerate(events, 1):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            event_details.append(
                f"{i}. Summary: {event.get('summary', 'No Title')}\n"
                f"   Start: {start}\n"
                f"   End: {end}\n"
                f"   Event ID: {event['id']}"
            )

        return "Upcoming Events:\n" + "\n\n".join(event_details)

    except HttpError as error:
        return f"An error occurred while listing events: {error}"

@tool
def create_event(summary: str, start_time: str, end_time: str, description: Optional[str] = None, calendar_id: Optional[str] = None):
    """
    Create a new event in the specified calendar.

    Args:
        summary (str): Event title
        start_time (str): Start time of the event (ISO format: YYYY-MM-DDTHH:MM:SS)
        end_time (str): End time of the event (ISO format: YYYY-MM-DDTHH:MM:SS)
        description (Optional[str]): Event description
        calendar_id (Optional[str]): ID of the calendar to create event in (default: primary)

    Returns:
        str: Confirmation message or error details
    """
    try:
        service = get_calendar_service()

        # Use primary calendar if no ID is provided
        if not calendar_id:
            calendar_id = 'primary'

        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        # Add description if provided
        if description:
            event['description'] = description

        event = service.events().insert(
            calendarId=calendar_id, 
            body=event
        ).execute()

        return (
            f"Event created successfully!\n"
            f"Event ID: {event['id']}\n"
            f"Event Link: {event.get('htmlLink', 'No link available')}"
        )

    except HttpError as error:
        return f"An error occurred while creating event: {error}"

@tool
def update_event(event_id: str, calendar_id: Optional[str] = None, summary: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, description: Optional[str] = None):
    """
    Update an existing event in the specified calendar.

    Args:
        event_id (str): ID of the event to update
        calendar_id (Optional[str]): ID of the calendar (default: primary)
        summary (Optional[str]): New event title
        start_time (Optional[str]): New start time (ISO format: YYYY-MM-DDTHH:MM:SS)
        end_time (Optional[str]): New end time (ISO format: YYYY-MM-DDTHH:MM:SS)
        description (Optional[str]): New event description

    Returns:
        str: Confirmation message or error details
    """
    try:
        service = get_calendar_service()

        # Use primary calendar if no ID is provided
        if not calendar_id:
            calendar_id = 'primary'

        # Retrieve the existing event first
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Update fields if provided
        if summary:
            event['summary'] = summary
        if description is not None:
            event['description'] = description
        if start_time:
            event['start']['dateTime'] = start_time
        if end_time:
            event['end']['dateTime'] = end_time

        # Update the event
        updated_event = service.events().update(
            calendarId=calendar_id, 
            eventId=event_id, 
            body=event
        ).execute()

        return (
            f"Event updated successfully!\n"
            f"Event ID: {updated_event['id']}\n"
            f"Event Link: {updated_event.get('htmlLink', 'No link available')}"
        )

    except HttpError as error:
        return f"An error occurred while updating event: {error}"

@tool
def delete_event(event_id: str, calendar_id: Optional[str] = None):
    """
    Delete an existing event from the specified calendar.

    Args:
        event_id (str): ID of the event to delete
        calendar_id (Optional[str]): ID of the calendar (default: primary)

    Returns:
        str: Confirmation message or error details
    """
    try:
        service = get_calendar_service()

        # Use primary calendar if no ID is provided
        if not calendar_id:
            calendar_id = 'primary'

        service.events().delete(
            calendarId=calendar_id, 
            eventId=event_id
        ).execute()

        return f"Event with ID {event_id} deleted successfully from calendar {calendar_id}."

    except HttpError as error:
        return f"An error occurred while deleting event: {error}"