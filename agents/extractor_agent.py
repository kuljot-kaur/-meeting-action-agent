"""
Extractor Agent
Takes a raw meeting transcript and extracts structured action items:
who owns what, what was decided, and any deadlines mentioned.
"""
import os
import time
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

EXTRACTION_PROMPT = """You are an assistant that extracts structured action items from meeting transcripts.

Read the transcript below and return ONLY valid JSON (no markdown, no commentary) in this exact schema:

{{
  "meeting_title": "string",
  "date": "string (YYYY-MM-DD if mentioned, else null)",
  "decisions": ["list of key decisions made"],
  "action_items": [
    {{
      "task": "string",
      "owner": "string (person's name)",
      "deadline": "string (YYYY-MM-DD if mentioned, else null)",
      "context": "string (one sentence of context)"
    }}
  ],
  "future_meetings": [
    {{
      "title": "string (name of the meeting/event mentioned)",
      "date": "string (YYYY-MM-DD, infer year 2026 if not stated)",
      "time": "string (HH:MM in 24hr format, default 09:00 if not stated)",
      "attendee_or_presenter": "string (who is presenting/attending, if mentioned)",
      "notes": "string (brief context)"
    }}
  ]
}}

Only include an entry in "future_meetings" if a specific future meeting or event with a date is explicitly mentioned in the transcript (not the current meeting itself).

Transcript:
{transcript}
"""


def extract_action_items(transcript_text: str, max_retries=4) -> dict:
    prompt = EXTRACTION_PROMPT.format(transcript=transcript_text)

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            return json.loads(raw_text)

        except Exception as e:
            last_error = e
            wait_time = 2 ** attempt  # 1, 2, 4, 8 seconds
            print(f"Attempt {attempt + 1} failed ({e}). Retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise RuntimeError(f"Failed after {max_retries} attempts. Last error: {last_error}")


if __name__ == "__main__":
    with open("data/sample_transcript.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    result = extract_action_items(transcript)
    print(json.dumps(result, indent=2))