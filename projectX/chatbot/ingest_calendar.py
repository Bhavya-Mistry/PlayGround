import os
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag import add_document
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
    """Authenticate with Google Calendar."""
    creds = None

    if os.path.exists("token_calendar.pickle"):
        with open("token_calendar.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token_calendar.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def format_event(event):
    """Format calendar event for storage."""
    summary = event.get("summary", "No Title")

    # Get start and end times
    start = event["start"].get("dateTime") or event["start"].get("date")
    end = event["end"].get("dateTime") or event["end"].get("date")

    description = event.get("description", "No description")
    location = event.get("location", "No location")
    organizer = event.get("organizer", {}).get("email", "Unknown")

    # Format attendees
    attendees = []
    if "attendees" in event:
        attendees = [a.get("email", "Unknown") for a in event["attendees"]]

    attendees_str = ", ".join(attendees) if attendees else "No attendees"

    # Create comprehensive document
    doc_text = f"""
EVENT: {summary}

TIME: {start} to {end}
LOCATION: {location}
ORGANIZER: {organizer}
ATTENDEES: {attendees_str}

DESCRIPTION:
{description}
"""

    return {
        "text": doc_text,
        "summary": summary,
        "start": str(start),
        "end": str(end),
        "location": location,
        "organizer": organizer,
    }


def ingest_calendar(days_ahead=90, max_results=50):
    """
    Fetch calendar events and add to Supabase.

    Args:
        days_ahead: How many days in the future to fetch
        max_results: Maximum number of events to fetch
    """
    print("📅 Starting Google Calendar ingestion...")

    try:
        service = get_calendar_service()
        print("✅ Connected to Google Calendar")

        # Get events from now until days_ahead
        now = datetime.utcnow().isoformat() + "Z"
        end_date = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

        # Fetch events
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=end_date,
                maxResults=min(max_results, 250),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        print(f"📅 Found {len(events)} calendar events")

        if not events:
            print("ℹ️  No events found")
            return

        success_count = 0

        for idx, event in enumerate(events, 1):
            try:
                formatted = format_event(event)

                success = add_document(
                    text=formatted["text"],
                    metadata={
                        "source": "calendar",
                        "subject": formatted["summary"],
                        "from": formatted["organizer"],
                        "date": formatted["start"],
                        "location": formatted["location"],
                        "event_id": event["id"],
                    },
                )

                if success:
                    success_count += 1

                print(f"  [{idx}/{len(events)}] ✅ {formatted['summary']}")

            except Exception as e:
                print(f"  [{idx}/{len(events)}] ⚠️  Error: {str(e)}")

        print(f"\n✅ Calendar ingestion complete! Added {success_count} events")

    except Exception as e:
        print(f"❌ Error: {e}")


def ingest_past_events(days_back=30, max_results=50):
    """
    Fetch past calendar events for context.

    Args:
        days_back: How many days in the past to fetch
        max_results: Maximum number of events to fetch
    """
    print("📅 Starting Past Events ingestion...")

    try:
        service = get_calendar_service()

        # Get past events
        end_date = datetime.utcnow().isoformat() + "Z"
        start_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_date,
                timeMax=end_date,
                maxResults=min(max_results, 250),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        print(f"📅 Found {len(events)} past events")

        if not events:
            print("ℹ️  No past events found")
            return

        success_count = 0

        for idx, event in enumerate(events, 1):
            try:
                formatted = format_event(event)

                success = add_document(
                    text=formatted["text"],
                    metadata={
                        "source": "calendar_past",
                        "subject": formatted["summary"],
                        "from": formatted["organizer"],
                        "date": formatted["start"],
                        "location": formatted["location"],
                        "event_id": event["id"],
                    },
                )

                if success:
                    success_count += 1

                print(f"  [{idx}/{len(events)}] ✅ {formatted['summary']}")

            except Exception as e:
                print(f"  [{idx}/{len(events)}] ⚠️  Error: {str(e)}")

        print(f"\n✅ Past events ingestion complete! Added {success_count} events")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Choose what to ingest:")
    print("1. Future events (default)")
    print("2. Past events")
    print("3. Both")
    choice = input("Enter choice (1-3) [default: 1]: ").strip() or "1"

    if choice == "1":
        ingest_calendar(days_ahead=90, max_results=50)
    elif choice == "2":
        ingest_past_events(days_back=30, max_results=50)
    elif choice == "3":
        ingest_calendar(days_ahead=90, max_results=50)
        ingest_past_events(days_back=30, max_results=50)
    else:
        print("Invalid choice")
