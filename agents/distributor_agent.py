"""
Distributor Agent
Takes structured action items (from the Extractor Agent) and creates:
- A Google Task for each action item
- A Calendar event if a deadline/date is mentioned
"""
import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/drive.file",
]

def get_credentials():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return creds

def get_or_create_tasklist(tasks_service, title="Meeting Action Items"):
    tasklists = tasks_service.tasklists().list().execute().get("items", [])
    for tl in tasklists:
        if tl["title"] == title:
            return tl["id"]
    new_list = tasks_service.tasklists().insert(body={"title": title}).execute()
    return new_list["id"]

def create_task(tasks_service, tasklist_id, action_item, meeting_title):
    body = {
        "title": f"{action_item['task']} (from: {meeting_title})",
        "notes": f"Owner: {action_item['owner']}\nContext: {action_item['context']}",
    }
    if action_item.get("deadline"):
        # Google Tasks API expects RFC3339 timestamp
        body["due"] = f"{action_item['deadline']}T00:00:00.000Z"

    result = tasks_service.tasks().insert(tasklist=tasklist_id, body=body).execute()
    return result

def create_calendar_event(calendar_service, title, date_str, description):
    if not date_str:
        return None
    start = f"{date_str}T09:00:00"
    end = f"{date_str}T09:30:00"
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
    }
    result = calendar_service.events().insert(calendarId="primary", body=event).execute()
    return result

def distribute(extraction_result: dict):
    creds = get_credentials()
    tasks_service = build("tasks", "v1", credentials=creds)
    calendar_service = build("calendar", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    tasklist_id = get_or_create_tasklist(tasks_service)

    created_tasks = []
    for item in extraction_result["action_items"]:
        task = create_task(tasks_service, tasklist_id, item, extraction_result["meeting_title"])
        created_tasks.append(task)
        print(f"Created task: {task['title']}")

    created_events = []
    for meeting in extraction_result.get("future_meetings", []):
        event = create_calendar_event_v2(calendar_service, meeting)
        created_events.append(event)
        print(f"Created calendar event: {event['summary']} on {event['start']['dateTime']}")

    recap_url = create_recap_doc(docs_service, drive_service, extraction_result)
    print(f"Created recap doc: {recap_url}")

    return created_tasks, created_events, recap_url


def create_calendar_event_v2(calendar_service, meeting: dict):
    date_str = meeting["date"]
    time_str = meeting.get("time", "09:00")
    start = f"{date_str}T{time_str}:00"
    # naive 30-min duration
    hour, minute = map(int, time_str.split(":"))
    end_hour = hour + 1 if minute == 0 else hour + 1
    end = f"{date_str}T{end_hour:02d}:{minute:02d}:00"

    event = {
        "summary": meeting["title"],
        "description": f"{meeting.get('notes', '')} (Presenter/Attendee: {meeting.get('attendee_or_presenter', 'N/A')})",
        "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
    }
    return calendar_service.events().insert(calendarId="primary", body=event).execute()

def create_recap_doc(docs_service, drive_service, extraction_result: dict) -> str:
    """
    Creates a new Google Doc with a clean, human-readable meeting recap.
    Returns the doc's URL.
    """
    title = f"Recap: {extraction_result['meeting_title']}"
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    lines = []
    lines.append(f"{extraction_result['meeting_title']}\n")
    if extraction_result.get("date"):
        lines.append(f"Date: {extraction_result['date']}\n\n")

    lines.append("DECISIONS\n")
    for d in extraction_result.get("decisions", []):
        lines.append(f"• {d}\n")

    lines.append("\nACTION ITEMS\n")
    for item in extraction_result.get("action_items", []):
        deadline = f" (due {item['deadline']})" if item.get("deadline") else ""
        lines.append(f"• {item['task']} — {item['owner']}{deadline}\n")

    if extraction_result.get("future_meetings"):
        lines.append("\nUPCOMING MEETINGS\n")
        for m in extraction_result["future_meetings"]:
            lines.append(f"• {m['title']} — {m['date']} at {m['time']} (Presenter: {m.get('attendee_or_presenter', 'N/A')})\n")

    full_text = "".join(lines)

    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": full_text,
            }
        }
    ]
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


if __name__ == "__main__":
    import json
    from extractor_agent import extract_action_items

    with open("data/sample_transcript.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    result = extract_action_items(transcript)
    distribute(result)

