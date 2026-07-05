"""
Transcript Agent
Fetches a meeting transcript either from:
  - a Google Doc (real Meet transcript saved to Drive), or
  - a local .txt file (for testing/demo purposes)
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/drive.file",
]

def get_credentials():
    return Credentials.from_authorized_user_file("token.json", SCOPES)


def get_transcript_from_doc(doc_id: str) -> str:
    """
    Fetches and flattens the text content of a Google Doc (e.g. a Meet
    auto-generated transcript) into a single plain-text string.
    """
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().get(documentId=doc_id).execute()

    text_parts = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for elem in paragraph.get("elements", []):
            text_run = elem.get("textRun")
            if text_run and text_run.get("content"):
                text_parts.append(text_run["content"])

    return "".join(text_parts).strip()


def get_transcript_from_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def get_transcript(doc_id: str = None, filepath: str = None) -> str:
    """
    Unified entry point. Pass a Google Doc ID for a real transcript,
    or a local filepath for testing.
    """
    if doc_id:
        print(f"Fetching transcript from Google Doc: {doc_id}")
        return get_transcript_from_doc(doc_id)
    elif filepath:
        print(f"Reading transcript from local file: {filepath}")
        return get_transcript_from_file(filepath)
    else:
        raise ValueError("Must provide either doc_id or filepath.")


if __name__ == "__main__":
    # Test with the local sample file for now
    text = get_transcript(filepath="data/sample_transcript.txt")
    print("--- Transcript preview ---")
    print(text[:300])