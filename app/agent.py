import os
import json
import random
import logging
import httpx
from typing import List, Optional
from pydantic import BaseModel, Field
from .config import config

logger = logging.getLogger(__name__)

class Insight(BaseModel):
    why_it_matters: str
    actionable_insight: str
    relevance_score: int

class AnalyzedArticle(BaseModel):
    title: str
    link: str
    source: str
    insight: Insight

class InsightAgent:
    def __init__(self):
        self.persona = config.persona
        self.provider = config.ai.provider.lower()
        self.model = config.ai.model_id
        
        self.system_prompt = f"""
        You are {self.persona.name}, acting as {self.persona.role}.
        Your interests are: {', '.join(self.persona.interests)}.
        Your tone is: {self.persona.tone}.
        
        Analyze the provided news article and explain why it matters to you specifically.
        Be brief, insightful, and strategic.
        
        Output MUST be in JSON format with these exact keys:
        - "why_it_matters": (string)
        - "actionable_insight": (string)
        - "relevance_score": (integer 0-10)
        """

    def analyze_article(self, article_title: str, article_summary: str) -> Optional[Insight]:
        """Analyze an article using raw HTTP requests to OpenAI/Anthropic/Gemini."""
        
        # 1. Check for API key and handle Mock Mode
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY"
        }
        api_key = os.getenv(key_map.get(self.provider, ""))
        
        if not api_key:
            # Mock Insights for UI visualization
            return Insight(
                why_it_matters="This article highlights a major shift in modern engineering practices.",
                actionable_insight="Benchmark current project workflows against these new findings.",
                relevance_score=random.randint(4, 9)
            )

        # 2. Prepare Payload based on provider
        try:
            if self.provider == "openai":
                return self._call_openai(api_key, article_title, article_summary)
            elif self.provider == "anthropic":
                return self._call_anthropic(api_key, article_title, article_summary)
            elif self.provider == "gemini":
                return self._call_gemini(api_key, article_title, article_summary)
        except Exception as e:
            logger.error(f"API Error ({self.provider}): {e}")
            return None
            
        return None

    def _call_openai(self, key, title, summary):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Title: {title}\nSummary: {summary}"}
            ],
            "response_format": {"type": "json_object"}
        }
        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=payload, timeout=30.0)
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return Insight.model_validate_json(content)

    def _call_anthropic(self, key, title, summary):
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 512,
            "system": self.system_prompt,
            "messages": [
                {"role": "user", "content": f"Analyze this article and return ONLY JSON:\nTitle: {title}\nSummary: {summary}"}
            ]
        }
        with httpx.Client() as client:
            resp = client.post(url, headers=headers, json=payload, timeout=30.0)
            data = resp.json()
            content = data["content"][0]["text"]
            # Clean up potential markdown code blocks if the model puts them in
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return Insight.model_validate_json(content)

    def _call_gemini(self, key, title, summary):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{self.system_prompt}\n\nAnalyze this article:\nTitle: {title}\nSummary: {summary}"}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
            }
        }
        with httpx.Client() as client:
            resp = client.post(url, json=payload, timeout=30.0)
            data = resp.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return Insight.model_validate_json(content)
