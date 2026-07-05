"""
Meeting Action Agent — CLI
A simple command-line interface (an "agent skill") for running the pipeline.

Usage:
    python cli.py process --file data/sample_transcript.txt
    python cli.py process --doc-id <GOOGLE_DOC_ID>
    python cli.py process --file data/sample_transcript.txt --dry-run
"""
import argparse
import sys
import os

sys.path.append(os.path.dirname(__file__))
from orchestrator.main import run_pipeline


def cmd_process(args):
    run_pipeline(doc_id=args.doc_id, filepath=args.file, dry_run=args.dry_run)


def main():
    parser = argparse.ArgumentParser(
        prog="meeting-agent",
        description="Meeting-to-Action Agent — turns meeting transcripts into real tasks, calendar events, and recap docs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    process_parser = subparsers.add_parser("process", help="Process a meeting transcript")
    process_parser.add_argument("--file", help="Local transcript file path")
    process_parser.add_argument("--doc-id", help="Google Doc ID containing the transcript")
    process_parser.add_argument("--dry-run", action="store_true", help="Extract only, skip creating Tasks/Calendar/Docs")
    process_parser.set_defaults(func=cmd_process)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()