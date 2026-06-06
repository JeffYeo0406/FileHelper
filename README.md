# Simple File Helper

Upload PDF bank statements, CSV, or Excel files. Gemini AI extracts transactions. Download a clean 2-tab Excel workbook.

## Quick Start

### Prerequisites
- Python 3.11+
- A [Gemini API key](https://aistudio.google.com/apikey) (free tier works)

### Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python seed.py               # Creates database + default admin account
```

### Configure

Edit `.env` in the project root:
```
GEMINI_API_KEY=your_actual_key_here
SECRET_KEY=any_random_string
```

### Run

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/app/index.html**

Default login: `admin` / `changeme123`

### Windows One-Click

Double-click `start.bat` in the project root.

## Adding Templates

Drop a `.json` file in `backend/templates/`. See `transaction_status_inquiry.json` for the format. Restart the server to load it.
