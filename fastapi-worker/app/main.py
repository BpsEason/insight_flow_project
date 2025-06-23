from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.core.insight_flow_core import InsightFlowCore
from app.models.request_models import AnalysisRequestPayload, AnalysisResult, AnalysisResponse
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightFlow AI Worker API",
    description="This API primarily provides health checks. Main analysis logic is handled by the Redis consumer.",
    version="0.1.0",
)

# Although the main processing is in consumer.py, InsightFlowCore might still be useful
# for specific direct API calls or for testing purposes.
# Re-initialize InsightFlowCore if not done globally to prevent memory issues for long-running services
# Or you might pass it as a dependency.

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "InsightFlow AI Worker API"}

# This endpoint is kept for direct testing or if a synchronous fallback is needed.
# However, the primary flow is now via Redis Queue and consumer.py
@app.post("/analyze_sync")
async def analyze_text_sync(request: AnalysisRequestPayload):
    """
    (Synchronous) Endpoint to perform AI analysis directly.
    For development/testing or specific synchronous needs.
    The primary analysis flow is now via the Redis queue.
    """
    logger.info(f"(Sync) Received analysis request for task ID: {request.task_id}")
    try:
        # Initialize InsightFlowCore only when needed for sync calls
        insight_flow_local = InsightFlowCore({
            "OPENAI_API_KEY": settings.OPENAI_API_KEY,
            "HUGGINGFACE_API_TOKEN": settings.HUGGINGFACE_API_TOKEN,
            "summarizer_model_type": settings.SUMMARIZER_MODEL_TYPE,
            "sentiment_model_type": settings.SENTIMENT_MODEL_TYPE,
            "keyword_extractor_type": settings.KEYWORD_EXTRACTOR_TYPE,
            "intent_recognizer_type": settings.INTENT_RECOGNIZER_TYPE,
            "sentiment_model_name": settings.SENTIMENT_MODEL_NAME,
            "recommender_config": {
                "product_catalog_path": "/app/data/products.json",
                "customer_segments_path": "/app/data/segments.json"
            }
        })
        
        analysis_result_dict = insight_flow_local.process_customer_feedback(request.text_content)
        analysis_output = AnalysisResult(**analysis_result_dict) # Validate output

        logger.info(f"(Sync) Analysis completed for task ID: {request.task_id}")
        return AnalysisResponse(
            task_id=request.task_id,
            status="processed_sync",
            analysis_output=analysis_output
        )
    except Exception as e:
        logger.error(f"(Sync) Error processing task {request.task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process analysis synchronously: {e}")
