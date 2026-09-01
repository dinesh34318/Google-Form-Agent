from pydantic import BaseModel
from typing import List, Optional, Any

class FormQuestion(BaseModel):
    id: str
    question: str
    type: str
    required: bool
    options: Optional[List[str]] = None
    entry_id: Optional[str] = None

class AnalyzeRequest(BaseModel):
    form_url: str

class FormAnalysisResponse(BaseModel):
    form_title: str
    questions: List[FormQuestion]
    session_id: str

class AnswerDecision(BaseModel):
    question: str
    profile_field: Optional[str] = None
    answer: Optional[Any] = None
    confidence: float
    fill: bool
    reason: str

class GenerateAnswersRequest(BaseModel):
    questions: List[FormQuestion]

class GenerateAnswersResponse(BaseModel):
    answers: List[AnswerDecision]

class UrlGeneratorRequest(BaseModel):
    form_url: str

class UrlGeneratorResponse(BaseModel):
    prefilled_url: Optional[str] = None
