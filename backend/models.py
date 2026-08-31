from pydantic import BaseModel, Field
from typing import List, Optional, Any

class FormQuestion(BaseModel):
    id: str
    question: str
    type: str # text, paragraph, multiple_choice, dropdown, checkbox, date
    required: bool
    options: Optional[List[str]] = None

class FormAnalysisResponse(BaseModel):
    form_title: str
    questions: List[FormQuestion]

class AnalyzeRequest(BaseModel):
    form_url: str

class GenerateAnswersRequest(BaseModel):
    questions: List[FormQuestion]

class AnswerDecision(BaseModel):
    question: str
    profile_field: Optional[str] = None
    answer: Optional[Any] = None
    confidence: float
    needs_user_input: bool
    reason: str

class GenerateAnswersResponse(BaseModel):
    answers: List[AnswerDecision]

class UserAnswer(BaseModel):
    id: str
    question: str
    answer: Any

class FillFormRequest(BaseModel):
    form_url: str
    answers: List[UserAnswer]

class FillFormResponse(BaseModel):
    status: str
    session_id: str
    message: Optional[str] = None
