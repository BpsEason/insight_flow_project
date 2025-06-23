import pytest
from app.core.insight_flow_core import InsightFlowCore, GPTSummarizer, HFSentimentAnalyzer, KeyBERTKeywordExtractor, OpenAIIntentRecognizer, RuleBasedRecommender
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_config():
    # Provide a mock configuration for InsightFlowCore
    return {
        "OPENAI_API_KEY": "mock_openai_key",
        "HUGGINGFACE_API_TOKEN": "mock_hf_token",
        "summarizer_model_type": "gpt_summarizer",
        "sentiment_model_type": "hf_sentiment_analyzer",
        "keyword_extractor_type": "keybert_extractor",
        "intent_recognizer_type": "openai_function_calling_recognizer",
        "sentiment_model_name": "mock-hf-model",
        "recommender_config": {
            "product_catalog_path": "/app/data/products.json",
            "customer_segments_path": "/app/data/segments.json"
        }
    }

@pytest.fixture
def insight_flow_core(mock_config):
    # Patch the concrete implementations so we don't need actual API calls/heavy models
    with patch('app.core.insight_flow_core.GPTSummarizer', autospec=True) as MockGPTSummarizer, \
         patch('app.core.insight_flow_core.HFSentimentAnalyzer', autospec=True) as MockHFSentimentAnalyzer, \
         patch('app.core.insight_flow_core.KeyBERTKeywordExtractor', autospec=True) as MockKeyBERTKeywordExtractor, \
         patch('app.core.insight_flow_core.OpenAIIntentRecognizer', autospec=True) as MockOpenAIIntentRecognizer, \
         patch('app.core.insight_flow_core.RuleBasedRecommender', autospec=True) as MockRuleBasedRecommender:

        # Configure mock return values
        MockGPTSummarizer.return_value.summarize.return_value = ["Mock summary."]
        MockHFSentimentAnalyzer.return_value.analyze.return_value = {"label": "neutral", "score": 0.5}
        MockKeyBERTKeywordExtractor.return_value.extract.return_value = ["mock_keyword"]
        MockOpenAIIntentRecognizer.return_value.recognize.return_value = {"intent": "general"}
        MockRuleBasedRecommender.return_value.generate_recommendations.return_value = ["Mock recommendation."]

        yield InsightFlowCore(mock_config) # Yield the actual Core class instance

def test_process_customer_feedback_success(insight_flow_core):
    test_input = "這是一段測試文字，關於客戶的意見。"
    result = insight_flow_core.process_customer_feedback(test_input)

    assert "摘要" in result
    assert "推薦" in result
    assert "情緒分數" in result
    assert "關鍵字" in result
    assert "意圖" in result

    assert result["摘要"] == ["Mock summary."]
    assert result["情緒分數"]["label"] == "neutral"
    assert result["關鍵字"] == ["mock_keyword"]
    assert result["意圖"]["intent"] == "general"
    assert result["推薦"] == ["Mock recommendation."]

    # Verify that the underlying module methods were called
    insight_flow_core.summarizer.summarize.assert_called_once_with(test_input)
    insight_flow_core.sentiment_analyzer.analyze.assert_called_once_with(test_input)
    insight_flow_core.keyword_extractor.extract.assert_called_once_with(test_input)
    insight_flow_core.intent_recognizer.recognize.assert_called_once_with(test_input)
    # Recommender's args are from previous steps, so assert with correct structure
    insight_flow_core.recommender.generate_recommendations.assert_called_once_with(
        summary=["Mock summary."],
        sentiment={"label": "neutral", "score": 0.5},
        keywords=["mock_keyword"],
        intent={"intent": "general"}
    )

def test_process_customer_feedback_error_handling(mock_config):
    with patch('app.core.insight_flow_core.GPTSummarizer', autospec=True) as MockGPTSummarizer:
        MockGPTSummarizer.return_value.summarize.side_effect = Exception("API error from summarizer")
        
        core = InsightFlowCore(mock_config)
        
        with pytest.raises(Exception, match="API error from summarizer"):
            core.process_customer_feedback("some text")

