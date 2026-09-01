from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

from models import (
    AnalyzeRequest, FormAnalysisResponse, 
    GenerateAnswersRequest, GenerateAnswersResponse,
    UrlGeneratorRequest, UrlGeneratorResponse
)
from form_reader import extract_form_data, close_session
from agent import decide_answers
from url_generator import generate_prefilled_url

app = FastAPI(title="FormAgent API")

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
        data = await extract_form_data(req.form_url)
        # Immediately close session, no longer needed
        await close_session(data["session_id"])
        
        return FormAnalysisResponse(
            form_title=data["form_title"],
            questions=data["questions"],
            session_id=data["session_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-answers", response_model=GenerateAnswersResponse)
async def get_answers(req: GenerateAnswersRequest):
    try:
        decisions = await decide_answers(req.questions)
        return GenerateAnswersResponse(answers=decisions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-prefilled-url", response_model=UrlGeneratorResponse)
async def get_prefilled_url(req: UrlGeneratorRequest):
    try:
        url = generate_prefilled_url(req.form_url, req.questions, req.answers)
        return UrlGeneratorResponse(prefilled_url=url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
