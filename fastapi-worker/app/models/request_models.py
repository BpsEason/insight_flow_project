from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class AnalysisRequestPayload(BaseModel):
    task_id: str
    text_content: str

class AnalysisResult(BaseModel):
    summary: List[str]
    recommendations: List[str]
    sentiment_score: Dict[str, float]
    keywords: List[str]
    intent: Optional[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    task_id: str
    status: str
    analysis_output: AnalysisResult # Nested Pydantic model for output
