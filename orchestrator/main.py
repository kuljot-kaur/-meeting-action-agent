"""
Orchestrator
Coordinates the full pipeline:
  1. Transcript Agent  -> fetches raw transcript text
  2. Extractor Agent    -> turns it into structured action items (Gemini)
  3. Distributor Agent  -> creates real Google Tasks + Calendar events

This is the multi-agent coordination layer for the Meeting-to-Action Agent.
"""
import sys
import os
import json
import argparse

# Allow importing from sibling 'agents' folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.transcript_agent import get_transcript
from agents.extractor_agent import extract_action_items
from agents.distributor_agent import distribute


def run_pipeline(doc_id: str = None, filepath: str = None, dry_run: bool = False):
    print("=" * 50)
    print("STEP 1/3: Transcript Agent")
    print("=" * 50)
    transcript_text = get_transcript(doc_id=doc_id, filepath=filepath)
    print(f"Transcript length: {len(transcript_text)} characters\n")

    print("=" * 50)
    print("STEP 2/3: Extractor Agent (Gemini)")
    print("=" * 50)
    extraction_result = extract_action_items(transcript_text)
    print(json.dumps(extraction_result, indent=2))
    print()

    print("=" * 50)
    print("STEP 3/3: Distributor Agent")
    print("=" * 50)
    if dry_run:
        print("[DRY RUN] Skipping actual Task/Calendar/Doc creation.")
        print(f"Would create {len(extraction_result.get('action_items', []))} tasks")
        print(f"Would create {len(extraction_result.get('future_meetings', []))} calendar events")
    else:
        created_tasks, created_events = distribute(extraction_result)
        print(f"\nDone. Created {len(created_tasks)} tasks and {len(created_events)} calendar events.")
    return extraction_result


def main():
    parser = argparse.ArgumentParser(description="Meeting-to-Action Agent pipeline")
    parser.add_argument("--doc-id", help="Google Doc ID containing the meeting transcript")
    parser.add_argument("--file", help="Local file path to a transcript (for testing)")
    parser.add_argument("--dry-run", action="store_true", help="Extract only, don't create Tasks/Calendar events")

    args = parser.parse_args()

    if not args.doc_id and not args.file:
        print("No input given, defaulting to local sample transcript (data/sample_transcript.txt)")
        args.file = "data/sample_transcript.txt"

    run_pipeline(doc_id=args.doc_id, filepath=args.file, dry_run=args.dry_run)


if __name__ == "__main__":
    main()