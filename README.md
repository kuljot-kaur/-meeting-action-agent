# 🤖 Meeting-to-Action Agent

An intelligent, production-ready system that takes meeting transcripts, extracts structured action items using Gemini, and provides an interactive dashboard to visualize the results and manage execution history. The project is fully containerized and deployed to **Google Cloud Run**.

## 🌟 Features

- **Interactive Dashboard**: A modern web UI to upload meeting transcripts (via pasting text, uploading `.txt` files, or importing from Google Doc IDs).
- **Gemini-Powered Extraction**: Utilizes the Google Gemini API to extract:
  - Meeting Title & Date
  - Key Decisions
  - Structured Action Items (task, owner, deadline, context)
  - Future Meetings (title, date, time, attendees, notes)
- **Extensible Pipeline**: Built with modular agent architecture:
  - `Transcript Agent`: Fetches/reads transcripts.
  - `Extractor Agent`: Performs Gemini AI analysis.
  - `Distributor Agent`: Standardized output formatting (with placeholder support for calendar/task sync).
- **History Dashboard**: Keeps a local history log of all processed meetings, decisions, and tasks.
- **Production Ready**: Optimized for Google Cloud Run deployment.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.13, Flask
- **AI/LLM**: Google Gemini SDK (`google-genai`)
- **Frontend**: Vanilla HTML5, CSS3 (sleek dark mode design), JavaScript
- **Infrastructure**: Google Cloud Run, Docker

---

## 📁 Project Structure

```text
├── agents/                 # Pipeline agents
│   ├── transcript_agent.py # Fetches text inputs
│   ├── extractor_agent.py  # Gemini AI extraction logic
│   └── distributor_agent.py# Handles output distributions
├── data/                   # Schema blueprints and run history
│   └── action_items_schema.json
├── static/                 # Frontend assets
│   └── dashboard.html      # UI Dashboard
├── Dockerfile              # Cloud Run container definition
├── requirements.txt        # Python package dependencies
├── server.py               # Flask application entry point
├── cli.py                  # CLI entry point for local tests
└── README.md               # Project documentation
```

---

## 🚀 Local Setup

### 1. Prerequisites
- Python 3.13+ installed.
- A Gemini API Key from Google AI Studio.

### 2. Install Dependencies
Clone the repository and install the required libraries:
```bash
# Clone the repository
git clone https://github.com/kuljot-kaur/-meeting-action-agent.git
cd -meeting-action-agent

# Create a virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
```bash
python server.py
```
Open your browser and navigate to `http://localhost:8080` to access the dashboard.

---

## 🌐 API Reference

### `GET /api/health`
Checks the server status.

**Response:**
```json
{
  "status": "ok",
  "service": "meeting-action-agent"
}
```

### `POST /api/extract`
Extracts action items from a raw transcript text.

**Request Body:**
```json
{
  "transcript": "Meeting transcript text goes here..."
}
```

### `POST /api/process`
Runs the full extraction and logs it to local run history.

**Request Body:**
```json
{
  "transcript": "Meeting transcript text...",
  "doc_id": "optional_google_doc_id",
  "dry_run": true
}
```

### `GET /api/history`
Retrieves past run records.

---

## ☁️ Cloud Run Deployment

To deploy this service to Google Cloud Run, run:

```bash
gcloud run deploy meeting-action-agent \
    --source . \
    --region us-central1 \
    --project meeting-action-agent-501417 \
    --allow-unauthenticated
```
