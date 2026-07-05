"""
Flask server — exposes the pipeline as an API and serves the dashboard.
"""
import os
import json
import datetime
from flask import Flask, request, jsonify, send_from_directory
from agents.transcript_agent import get_transcript
from agents.extractor_agent import extract_action_items
from agents.distributor_agent import distribute

app = Flask(__name__, static_folder="static")

HISTORY_FILE = "data/history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


@app.route("/")
def dashboard():
    return send_from_directory("static", "dashboard.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "meeting-action-agent"})


@app.route("/api/extract", methods=["POST"])
def extract_only():
    data = request.get_json(force=True)
    transcript_text = data.get("transcript")
    if not transcript_text:
        return jsonify({"error": "Missing 'transcript' field"}), 400
    try:
        result = extract_action_items(transcript_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/process", methods=["POST"])
def process():
    """
    Full pipeline: transcript -> extraction -> (optionally) real
    Tasks/Calendar/Docs creation. Requires token.json to exist locally
    for the distribute step (real Google account write access).
    """
    data = request.get_json(force=True)
    transcript_text = data.get("transcript")
    doc_id = data.get("doc_id")
    dry_run = data.get("dry_run", True)

    if not transcript_text and not doc_id:
        return jsonify({"error": "Provide either 'transcript' or 'doc_id'"}), 400

    try:
        if doc_id:
            transcript_text = get_transcript(doc_id=doc_id)

        extraction_result = extract_action_items(transcript_text)

        tasks_created = 0
        events_created = 0
        recap_url = None

        if not dry_run:
            created_tasks, created_events, recap_url = distribute(extraction_result)
            tasks_created = len(created_tasks)
            events_created = len(created_events)

        history = load_history()
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "meeting_title": extraction_result.get("meeting_title") or "Untitled meeting",
            "decisions_count": len(extraction_result.get("decisions", [])),
            "action_items_count": len(extraction_result.get("action_items", [])),
            "tasks_created": tasks_created,
            "events_created": events_created,
            "recap_url": recap_url,
            "dry_run": dry_run,
            "extraction": extraction_result,
        }
        history.insert(0, entry)
        save_history(history)

        return jsonify(entry)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def history():
    return jsonify(load_history())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)