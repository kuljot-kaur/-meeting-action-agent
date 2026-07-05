"""
Quick test to confirm OAuth works and we can talk to Google APIs.
Run this once to generate token.json (cached credentials for future runs).
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/drive.file",
]

def main():
    creds = None
    if os.path.exists("token.json"):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Quick sanity check: list next 5 calendar events
    service = build("calendar", "v3", credentials=creds)
    events_result = service.events().list(
        calendarId="primary", maxResults=5, singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    print("Auth successful! Here are your next few calendar events:")
    if not events:
        print("  (no upcoming events found)")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"  - {start}: {event.get('summary', '(no title)')}")

if __name__ == "__main__":
    main()