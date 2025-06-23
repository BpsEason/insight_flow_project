import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HUGGINGFACE_API_TOKEN: str = os.getenv("HUGGINGFACE_API_TOKEN", "")

    # AI Model Configurations (for plug-in architecture)
    SUMMARIZER_MODEL_TYPE: str = "gpt_summarizer" # Options: "gpt_summarizer", "hf_summarizer", "rule_based_summarizer"
    SENTIMENT_MODEL_TYPE: str = "hf_sentiment_analyzer" # Options: "hf_sentiment_analyzer", "custom_sentiment_analyzer"
    KEYWORD_EXTRACTOR_TYPE: str = "keybert_extractor" # Options: "keybert_extractor", "llm_keyword_extractor"
    INTENT_RECOGNIZER_TYPE: str = "openai_function_calling_recognizer" # Options: "openai_function_calling_recognizer", "custom_intent_recognizer"

    SENTIMENT_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst2" # Specific HF model name

    # Redis Configuration for worker consumer
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_QUEUE_NAME: str = "fastapi_analysis_queue"

settings = Settings()
