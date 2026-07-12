# Meeting-to-Action Agent

**Track:** Freestyle
**Built with:** Google Antigravity, Gemini (AI Studio), Google Cloud Run, Google Workspace APIs (Calendar, Tasks, Docs, Drive), MCP

## Problem

Meetings generate decisions and action items, but they routinely get lost. Notes sit in a
transcript or a doc that nobody reopens, tasks never make it onto anyone's to-do list, and
follow-up meetings don't get scheduled. This creates a silent tax on every team: decisions
made in a meeting quietly evaporate unless someone manually does the busywork of turning
talk into tracked action.

## Solution

The Meeting-to-Action Agent is a multi-agent system that takes a raw meeting transcript
(from a local file, or a real Google Doc — e.g. an auto-saved Google Meet transcript) and
automatically:

1. Extracts decisions, action items (with owners and deadlines), and any future meetings mentioned
2. Creates real Google Tasks for each action item
3. Creates real Google Calendar events for any future meetings mentioned
4. Generates a clean, human-readable recap in a new Google Doc

No human has to manually re-type action items into a task tracker or calendar ever again.

## Architecture

```
Transcript Agent  -->  Extractor Agent (Gemini)  -->  Distributor Agent
(Google Doc/file)      (structured JSON output)       (Tasks + Calendar + Docs)
        \______________________ Orchestrator ______________________/
                     (coordinates the full pipeline)
```

- **Transcript Agent** (`agents/transcript_agent.py`): Fetches transcript text either from
  a Google Doc (via Docs API) or a local file.
- **Extractor Agent** (`agents/extractor_agent.py`): Sends the transcript to Gemini
  (`gemini-2.5-flash`) with a structured-output prompt, returning decisions, action items
  (task/owner/deadline/context), and any future meetings mentioned. Includes exponential
  backoff retry logic for API resilience.
- **Distributor Agent** (`agents/distributor_agent.py`): Takes the structured output and
  creates real Google Tasks, Calendar events, and a recap Google Doc via their respective APIs.
- **Orchestrator** (`orchestrator/main.py`): Coordinates the full pipeline end to end, with
  a `--dry-run` mode for safe testing.
- **CLI** (`cli.py`): A packaged command-line interface (`python cli.py process ...`) — the
  project's "agent skill" layer.
- **Server** (`server.py`): A Flask wrapper exposing the Extractor Agent as a stateless HTTP
  API, deployed to Cloud Run.

## Security

- OAuth 2.0 (not hardcoded credentials) is used for all Google Workspace API access, scoped
  to only the four scopes required (Calendar, Tasks, Docs, Drive.file).
- `credentials.json` and `token.json` are excluded from version control via `.gitignore`.
- The deployed Cloud Run service exposes only the stateless Extractor Agent (transcript in,
  structured JSON out) — it does not have access to any individual's personal Tasks,
  Calendar, or Docs. Writing to a specific user's Google Workspace data requires that
  user's own OAuth consent, run locally — a deliberate boundary so the publicly deployed
  service cannot act on anyone's personal account without their explicit authorization.
- Deployment itself required explicit human approval at each MCP tool-call step (visible in
  the Antigravity CLI session), rather than being able to run unattended cloud actions
  without consent.

## Setup Instructions

### Prerequisites
- Python 3.11+
- A Google Cloud project with the Calendar, Tasks, Docs, and Drive APIs enabled
- A Gemini API key from [AI Studio](https://aistudio.google.com/apikey)
- (Optional, for redeployment) [Antigravity CLI](https://antigravity.google) and a linked
  GCP billing account

### Local setup

```bash
git clone <your-repo-url>
cd meeting-action-agent
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

python -m pip install -r requirements.txt
```

1. Create OAuth credentials (Desktop app type) in Google Cloud Console and save as `credentials.json` in the project root.
2. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`.
3. Run the auth test once to generate `token.json`:
   ```bash
   python test_auth.py
   ```

### Running the pipeline

```bash
# Process a local sample transcript (safe dry run)
python cli.py process --file data/sample_transcript.txt --dry-run

# Process for real (creates actual Tasks/Calendar events/Doc)
python cli.py process --file data/sample_transcript.txt

# Process a real Google Doc transcript
python cli.py process --doc-id <YOUR_GOOGLE_DOC_ID>
```

### Deployment

The project includes a `Dockerfile` and `server.py` for deployment as a Cloud Run service.
It was deployed using the Antigravity CLI's Cloud Run MCP server:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
agy
> Deploy this folder as a Cloud Run service named meeting-action-agent in us-central1.
```

Live deployed instance (extraction endpoint only): `https://meeting-action-agent-sitvwtsz6a-uc.a.run.app/extract`

## Course concepts demonstrated

| Concept | Where |
|---|---|
| Multi-agent system | `agents/`, `orchestrator/main.py` |
| MCP Server | Cloud Run MCP (deployment), plus Google Workspace APIs as agent tools |
| Antigravity | Used to orchestrate and execute the Cloud Run deployment |
| Security features | OAuth scoping, `.gitignore`'d credentials, stateless public endpoint boundary |
| Deployability | Live Cloud Run deployment, documented above |
| Agent skills (CLI) | `cli.py` |

## Project structure

```
meeting-action-agent/
├── agents/
│   ├── transcript_agent.py
│   ├── extractor_agent.py
│   └── distributor_agent.py
├── orchestrator/
│   └── main.py
├── cli.py
├── server.py
├── Dockerfile
├── data/
│   └── sample_transcript.txt
├── requirements.txt
└── README.md

