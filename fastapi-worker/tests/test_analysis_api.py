import pytest
from httpx import AsyncClient
from app.main import app # Import the FastAPI app
from app.config import settings # Import settings
import redis # Import redis for testing consumer

# Configure Redis for testing (different DB or mock if necessary)
# For integration tests with docker-compose, this will use the 'redis' service
TEST_REDIS_CLIENT = redis.Redis(host='redis', port=settings.REDIS_PORT, db=settings.REDIS_DB)


@pytest.fixture(autouse=True)
def cleanup_redis_queue():
    """Fixture to clear the Redis queue before each test."""
    TEST_REDIS_CLIENT.delete(settings.REDIS_QUEUE_NAME)
    yield
    TEST_REDIS_CLIENT.delete(settings.REDIS_QUEUE_NAME) # Ensure cleanup after test too

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "InsightFlow AI Worker API"}

@pytest.mark.asyncio
async def test_analyze_sync_endpoint():
    # This tests the /analyze_sync endpoint, not the primary queue-based flow.
    async with AsyncClient(app=app, base_url="http://test") as client:
        test_payload = {
            "task_id": "test-sync-uuid-123",
            "text_content": "顧客抱怨胃部不適，希望有促銷方案。"
        }
        response = await client.post("/analyze_sync", json=test_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-sync-uuid-123"
        assert data["status"] == "processed_sync"
        assert "analysis_output" in data
        assert "摘要" in data["analysis_output"]
        assert "推薦" in data["analysis_output"]
        assert "情緒分數" in data["analysis_output"]
        assert "關鍵字" in data["analysis_output"]
        assert "意圖" in data["analysis_output"]
