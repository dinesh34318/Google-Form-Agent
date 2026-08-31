import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any


from models import (
    AnalyzeRequest, FormAnalysisResponse,
    GenerateAnswersRequest, GenerateAnswersResponse,
    FillFormRequest, FillFormResponse, UserAnswer
)
from form_reader import extract_form_data, close_session, active_sessions
from agent import decide_answers
from form_filler import fill_form
from profile import update_preference

app = FastAPI(title="FormAgent API")

# Allow mobile app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze", response_model=FormAnalysisResponse)
async def analyze_form(req: AnalyzeRequest):
    try:
        result = await extract_form_data(req.form_url)
        return FormAnalysisResponse(
            form_title=result["form_title"],
            questions=result["questions"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-answers", response_model=GenerateAnswersResponse)
async def generate_answers(req: GenerateAnswersRequest):
    try:
        decisions = decide_answers(req.questions)
        return GenerateAnswersResponse(answers=decisions)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/fill", response_model=FillFormResponse)
async def fill_google_form(req: FillFormRequest):
    # Find active session based on form URL (MVP shortcut if mobile doesn't send session_id)
    # Ideally, we pass session_id from mobile.
    session_id = None
    for sid, session_data in active_sessions.items():
        if session_data["url"] == req.form_url:
            session_id = sid
            break
            
    if not session_id:
        # User might have restarted app or session died.
        # We need to re-open the form, but let's just error for now.
        raise HTTPException(status_code=400, detail="Active browser session not found. Please analyze again.")

    try:
        result = await fill_form(session_id, req.answers)
        return FillFormResponse(
            status=result["status"],
            session_id=session_id,
            message="Form filled successfully. Please review the browser window and manually submit."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/remember")
async def remember_answer(data: Dict[str, Any]):
    # Allow saving preferences
    if "key" in data and "value" in data:
        update_preference(data["key"], data["value"])
        return {"status": "saved"}
    raise HTTPException(status_code=400, detail="Invalid data")

@app.get("/session/{session_id}")
async def get_session_status(session_id: str):
    if session_id in active_sessions:
        return {"status": "active"}
    return {"status": "expired"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
