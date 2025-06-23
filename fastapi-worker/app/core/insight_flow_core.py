import os
import json
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod # For Abstract Base Classes
import logging

logger = logging.getLogger(__name__)

# --- Define Abstract Interfaces for AI Modules (Strategy Pattern) ---
class Summarizer(ABC):
    @abstractmethod
    def summarize(self, text: str) -> List[str]:
        pass

class SentimentAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, float]:
        pass

class KeywordExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, top_n: int = 5) -> List[str]:
        pass

class IntentRecognizer(ABC):
    @abstractmethod
    def recognize(self, text: str) -> Optional[Dict[str, Any]]:
        pass

class Recommender(ABC):
    @abstractmethod
    def generate_recommendations(self, summary: List[str], sentiment: Dict[str, float], keywords: List[str], intent: Optional[Dict[str, Any]]) -> List[str]:
        pass

# --- Concrete Implementations (Placeholders) ---
# These classes would live in fastapi-worker/app/modules/
# For brevity in this script, they are placed here.
# In a real project, import them like: from app.modules.summarizers.gpt_summarizer import GPTSummarizer

class GPTSummarizer(Summarizer):
    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API Key not set for GPTSummarizer.")
        # self.client = OpenAI(api_key=self.api_key) # Initialize OpenAI client

    def summarize(self, text: str) -> List[str]:
        # Mock logic, replace with actual OpenAI API call
        if "胃部不適" in text:
            return ["主要問題為「胃部不適與睡眠困擾」。", "約 40% 顧客有明確症狀表達。"]
        return [f"通用摘要: {text[:50]}..."]

class HFSentimentAnalyzer(SentimentAnalyzer):
    def __init__(self, model_name: str):
        self.model_name = model_name
        # self.pipeline = pipeline("sentiment-analysis", model=model_name)

    def analyze(self, text: str) -> Dict[str, float]:
        # Mock logic, replace with actual HuggingFace pipeline call
        if "不滿意" in text or "抱怨" in text: return {"label": "negative", "score": 0.95}
        if "感謝" in text or "滿意" in text: return {"label": "positive", "score": 0.98}
        return {"label": "neutral", "score": 0.8}

class KeyBERTKeywordExtractor(KeywordExtractor):
    def __init__(self):
        # from keybert import KeyBERT
        # self.kw_model = KeyBERT()
        pass
    def extract(self, text: str, top_n: int = 5) -> List[str]:
        keywords = []
        if "保健食品" in text: keywords.append("保健食品")
        if "胃部不適" in text: keywords.append("胃部不適")
        if "睡眠品質" in text: keywords.append("睡眠品質")
        if "促銷方案" in text: keywords.append("促銷方案")
        return keywords[:top_n]

class OpenAIIntentRecognizer(IntentRecognizer):
    def __init__(self, api_key: str = None):
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        # self.client = OpenAI(api_key=self.api_key)

    def recognize(self, text: str) -> Optional[Dict[str, Any]]:
        # Mock logic, replace with actual OpenAI Function Calling
        if "胃部不適" in text: return {"intent": "健康問題諮詢", "product_category": "腸胃照護產品"}
        if "睡眠品質" in text: return {"intent": "健康問題諮詢", "product_category": "睡眠產品"}
        if "促銷" in text: return {"intent": "促銷活動查詢"}
        return {"intent": "產品諮詢", "product_category": "保健食品"} # Default

class RuleBasedRecommender(Recommender):
    def __init__(self, product_catalog_path: str, customer_segments_path: str):
        self.product_catalog = self._load_json_data(product_catalog_path)
        self.customer_segments = self._load_json_data(customer_segments_path)

    def _load_json_data(self, file_path: str) -> Dict[str, Any]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        logger.warning(f"Data file not found: {file_path}")
        return {}

    def generate_recommendations(self, summary: List[str], sentiment: Dict[str, float], keywords: List[str], intent: Optional[Dict[str, Any]]) -> List[str]:
        recommendations = ["根據分析，建議："]
        summary_text = " ".join(summary)

        if intent and intent.get("product_category") == "睡眠產品":
            recommendations.append("寄送「睡眠系列產品」推薦郵件。")
        if intent and intent.get("product_category") == "腸胃照護產品":
            recommendations.append("觸發自動推薦「腸胃照護」商品模組。")
        if "促銷方案" in summary_text or (intent and intent.get("intent") == "促銷活動查詢"):
            recommendations.append("促銷訊息應優先展示在首頁。")
        if sentiment.get("label") == "negative" and sentiment.get("score", 0) > 0.8:
            recommendations.append("客戶情緒較為負面，建議人工介入。")

        return list(set(recommendations)) # Remove duplicates

# --- InsightFlow Core Class ---
class InsightFlowCore:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Initialize modules based on configuration (Strategy Pattern)
        self.summarizer = self._load_module(config.get("summarizer_model_type"), {
            "gpt_summarizer": GPTSummarizer,
            # "hf_summarizer": HFSummarizer, # Add actual HF summarizer class here
        }, api_key=config.get("OPENAI_API_KEY"))

        self.sentiment_analyzer = self._load_module(config.get("sentiment_model_type"), {
            "hf_sentiment_analyzer": HFSentimentAnalyzer,
        }, model_name=config.get("sentiment_model_name"))

        self.keyword_extractor = self._load_module(config.get("keyword_extractor_type"), {
            "keybert_extractor": KeyBERTKeywordExtractor,
        })

        self.intent_recognizer = self._load_module(config.get("intent_recognizer_type"), {
            "openai_function_calling_recognizer": OpenAIIntentRecognizer,
        }, api_key=config.get("OPENAI_API_KEY"))

        self.recommender = self._load_module("rule_based_recommender", { # Current fixed to rule-based
            "rule_based_recommender": RuleBasedRecommender,
        }, product_catalog_path=config.get("recommender_config", {}).get("product_catalog_path"),
           customer_segments_path=config.get("recommender_config", {}).get("customer_segments_path"))

    def _load_module(self, module_type: str, module_map: Dict[str, type], **kwargs):
        """Helper to load module based on type."""
        module_class = module_map.get(module_type)
        if not module_class:
            raise ValueError(f"Unknown module type: {module_type}")
        return module_class(**kwargs)

    def process_customer_feedback(self, user_input: str) -> Dict[str, Any]:
        """Processes customer feedback through various AI modules."""
        try:
            summary_output = self.summarizer.summarize(user_input)
            sentiment_score = self.sentiment_analyzer.analyze(user_input)
            keywords = self.keyword_extractor.extract(user_input)
            intent = self.intent_recognizer.recognize(user_input)
            recommendations = self.recommender.generate_recommendations(
                summary=summary_output,
                sentiment=sentiment_score,
                keywords=keywords,
                intent=intent
            )

            return {
                "摘要": summary_output,
                "推薦": recommendations,
                "情緒分數": sentiment_score,
                "關鍵字": keywords,
                "意圖": intent,
            }
        except Exception as e:
            logger.error(f"Error during feedback processing: {e}", exc_info=True)
            raise # Re-raise to be handled by caller
