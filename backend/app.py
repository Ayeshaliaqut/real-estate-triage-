#used fast api 
import os
import logging
from typing import List

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

from .scoring import compute_qualification_score, score_to_tier
from .llm_client import call_llm_for_intent

# load env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s %(levelname)s %(name)s - %(message)s")
LOGGER = logging.getLogger(__name__)

app = FastAPI(title="Real Estate Lead Triage (Backend)")
#intialize directories 
FRONTEND_TEMPLATES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
)
FRONTEND_STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
)
#statuc folder
if os.path.isdir(FRONTEND_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="static")
else:
    LOGGER.warning("Static directory not found: %s", FRONTEND_STATIC_DIR)

templates = Jinja2Templates(directory=FRONTEND_TEMPLATES_DIR)

# In-memory store for leads
LEADS_STORE: List[dict] = []

# Default CSV path
CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "test_leads_30.csv")
)

#routes
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        LOGGER.exception("Template load failed: %s", e)
        return HTMLResponse("Template missing.", status_code=500)


@app.post("/api/load_and_process")
def load_and_process(path: str = Form(None)):
    global LEADS_STORE
    csv_path = path or CSV_PATH

    LOGGER.info("Loading CSV from: %s", csv_path)

    if not os.path.exists(csv_path):
        return JSONResponse({"error": f"file not found: {csv_path}"}, status_code=400)

    # Load CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        LOGGER.exception("CSV read error: %s", e)
        return JSONResponse({"error": "failed to read CSV", "detail": str(e)}, status_code=500)

    processed = []

    for idx, row in df.iterrows():
        try:
            lead = {col: ("" if pd.isna(row[col]) else row[col]) for col in df.columns}

            # Scoring
            score, reasons = compute_qualification_score(lead)
            tier, action = score_to_tier(score)

            # LLM
            try:
                llm_info = call_llm_for_intent(lead) or {}
            except Exception as e:
                LOGGER.error("LLM failed for row %s: %s", idx, e)
                llm_info = {}

            result = {
                **lead,
                "qualification_score": int(score),
                "tier": tier,
                "recommended_action": action,
                "reasons": reasons,
                "intent_label": llm_info.get("intent_label", "casual_inquiry"),
                "short_reason": llm_info.get("short_reason", "")
            }

            processed.append(result)

        except Exception as e:
            LOGGER.exception("Row processing error: %s", e)
            continue

    LEADS_STORE = processed

    # Compute report
    totals = {}
    hot_counts = {}

    for l in LEADS_STORE:
        src = l.get("source", "unknown")
        totals[src] = totals.get(src, 0) + 1
        if l.get("tier") == "hot":
            hot_counts[src] = hot_counts.get(src, 0) + 1

    report = []
    for src, total in totals.items():
        hot = hot_counts.get(src, 0)
        pct = round((hot / total) * 100, 1)
        report.append({
            "source": src,
            "total": total,
            "hot_count": hot,
            "hot_pct": pct
        })

    return {
        "leads_count": len(LEADS_STORE),
        "report": report,
        "preview": LEADS_STORE[:10]
    }


@app.get("/api/leads")
def get_leads():
    return {"leads": LEADS_STORE}
