import redis
import json
import time
import logging
import os # Import os for environment variables
from app.core.insight_flow_core import InsightFlowCore
from app.config import settings
from app.models.request_models import AnalysisRequestPayload
import requests # To update Laravel backend

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Redis client
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

# Initialize InsightFlow core (assuming it's stateless and can be reused)
insight_flow = InsightFlowCore({
    "OPENAI_API_KEY": settings.OPENAI_API_KEY,
    "HUGGINGFACE_API_TOKEN": settings.HUGGINGFACE_API_TOKEN,
    "summarizer_model_type": settings.SUMMARIZER_MODEL_TYPE,
    "sentiment_model_type": settings.SENTIMENT_MODEL_TYPE,
    "keyword_extractor_type": settings.KEYWORD_EXTRACTOR_TYPE,
    "intent_recognizer_type": settings.INTENT_RECOGNIZER_TYPE,
    "sentiment_model_name": settings.SENTIMENT_MODEL_NAME,
    "recommender_config": {
        "product_catalog_path": "/app/data/products.json", # Docker container path
        "customer_segments_path": "/app/data/segments.json"
    }
})

def update_laravel_task_status(task_id: str, status: str, result: dict = None):
    """
    Sends an update back to the Laravel backend.
    """
    # This URL must be reachable from the FastAPI worker container to the Laravel app container.
    # 'app' is the service name in docker-compose, which resolves to the Laravel container's IP.
    laravel_update_url = os.getenv("LARAVEL_INTERNAL_UPDATE_URL", "http://app/api/internal/analysis/update")
    
    payload = {
        "task_id": task_id,
        "status": status,
        "result": result
    }
    try:
        response = requests.post(laravel_update_url, json=payload, timeout=30)
        response.raise_for_status() # Raise an exception for HTTP errors
        logger.info(f"Successfully updated Laravel for task {task_id} with status {status}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Laravel for task {task_id}: {e}")


def consume_tasks():
    logger.info(f"FastAPI worker starting to consume tasks from Redis queue: {settings.REDIS_QUEUE_NAME}")
    while True:
        # Blocking pop from list. Timeout 1 second.
        # This makes the consumer sleep if there are no tasks, reducing CPU usage.
        task_data_raw = r.brpop(settings.REDIS_QUEUE_NAME, timeout=1) 
        
        if task_data_raw:
            # task_data_raw returns a tuple: (queue_name, task_data_json_string)
            queue_name, task_json = task_data_raw
            task_id = None # Initialize for logging in case of parsing error
            try:
                payload = json.loads(task_json)
                request_payload = AnalysisRequestPayload(**payload)
                task_id = request_payload.task_id
                text_content = request_payload.text_content

                logger.info(f"Processing task: {task_id}")
                update_laravel_task_status(task_id, "processing") # Inform Laravel

                analysis_output = insight_flow.process_customer_feedback(text_content)
                
                # Success
                update_laravel_task_status(task_id, "completed", {"analysis_output": analysis_output})
                logger.info(f"Task {task_id} completed successfully.")

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from Redis: {task_json}. Error: {e}")
            except Exception as e:
                logger.error(f"Error processing task {task_id}: {e}", exc_info=True)
                update_laravel_task_status(task_id, "failed", {"error": str(e), "details": "Worker processing failed"})
        else:
            # No tasks in queue, sleep briefly before checking again
            time.sleep(0.5)

if __name__ == "__main__":
    consume_tasks()
