import os
import json
from typing import List, Dict, Any, Literal
from openai import OpenAI
from pydantic import BaseModel, Field
from models import FormQuestion, AnswerDecision
from profile import load_profile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CategoryResponse(BaseModel):
    category: Literal["personal", "education", "skills", "projects", "experience", "preferences", "none"]

class AgentResponse(BaseModel):
    profile_field: str | None = Field(description="The field path in the profile (e.g. personal.full_name), or null if not found")
    answer: Any | None = Field(description="The actual answer value to use, or null if unknown")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    needs_user_input: bool = Field(description="True if the user needs to provide or confirm this answer")
    reason: str = Field(description="Reasoning for this decision")

def decide_answers(questions: List[FormQuestion]) -> List[AnswerDecision]:
    profile_data = load_profile()
    decisions = []
    
    for q in questions:
        user_content = f"Question: {q.question}\nType: {q.type}\nRequired: {q.required}\nOptions: {q.options}"
        
        try:
            # Step 1: Categorize the question
            cat_prompt = f"""
You are an AI that categorizes form questions to determine which part of a user's profile is needed.
Available categories: {list(profile_data.keys())}
If none apply, output 'none'.
            """
            cat_resp = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": cat_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=CategoryResponse,
            )
            category = cat_resp.choices[0].message.parsed.category
            
            # Step 2: Extract answer using only the relevant category
            relevant_data = profile_data.get(category, {}) if category != "none" else {}
            
            system_prompt = f"""
You are FormAgent, a personal AI assistant that fills Google Forms for the user.
Your job is to match form questions to the provided personal profile data.
You MUST NEVER invent personal information. If the information is not in the data or cannot be confidently derived, set `needs_user_input` to true and `answer` to null.

Here is the relevant portion of the user's personal profile (JSON):
```json
{json.dumps({category: relevant_data}, indent=2)}
```

For multiple_choice, dropdown, and checkbox questions, your answer MUST match one (or more for checkboxes) of the provided options exactly.
If the data contains the answer but it needs to be mapped to an exact option (e.g., "Male" to "Male", or "3rd Year" to "3rd Year"), do so. If there is no matching option, set needs_user_input to true.
            """
            
            response = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=AgentResponse,
            )
            
            agent_resp = response.choices[0].message.parsed
            
            decision = AnswerDecision(
                question=q.question,
                profile_field=agent_resp.profile_field,
                answer=agent_resp.answer,
                confidence=agent_resp.confidence,
                needs_user_input=agent_resp.needs_user_input,
                reason=agent_resp.reason
            )
            
            # Validation for choices
            if decision.answer is not None and not decision.needs_user_input:
                if q.type in ["multiple_choice", "dropdown"] and q.options:
                    if decision.answer not in q.options:
                        decision.needs_user_input = True
                        decision.reason += " (Answer did not perfectly match available options)"
                elif q.type == "checkbox" and q.options:
                    if isinstance(decision.answer, list):
                        if not all(a in q.options for a in decision.answer):
                            decision.needs_user_input = True
                            decision.reason += " (Some checkbox answers did not match options)"
                    else:
                         if decision.answer not in q.options:
                             decision.needs_user_input = True
                             decision.reason += " (Answer did not perfectly match available options)"
                             
            decisions.append(decision)
            
        except Exception as e:
            decisions.append(AnswerDecision(
                question=q.question,
                profile_field=None,
                answer=None,
                confidence=0.0,
                needs_user_input=True,
                reason=f"Error generating answer: {str(e)}"
            ))
            
    return decisions
