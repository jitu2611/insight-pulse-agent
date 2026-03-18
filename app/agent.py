import litellm
import logging
import os
from typing import List, Optional
from pydantic import BaseModel, Field
from .config import config

# LiteLLM Setup
# This allows us to use gpt-4o, claude-3-5, gemini-1.5-pro, etc.
# By default, LiteLLM pulls keys from environment variables like OPENAI_API_KEY, etc.

class Insight(BaseModel):
    why_it_matters: str = Field(description="Why this article is relevant to the persona's interests and role.")
    actionable_insight: str = Field(description="A suggested action or specific thing to investigate further.")
    relevance_score: int = Field(ge=0, le=10, description="Rate relevance from 0-10.")

class AnalyzedArticle(BaseModel):
    title: str
    link: str
    source: str
    insight: Insight

def get_model_name() -> str:
    # Map friendly provider names to LiteLLM standard names
    provider = config.ai.provider.lower()
    model_id = config.ai.model_id
    
    if provider == "openai":
        return f"openai/{model_id}"
    elif provider == "anthropic":
        return f"anthropic/{model_id}"
    elif provider == "gemini":
        return f"gemini/{model_id}"
    return f"{provider}/{model_id}"

class InsightAgent:
    def __init__(self):
        self.model = get_model_name()
        self.persona = config.persona
        self.system_prompt = f"""
        You are {self.persona.name}, acting as {self.persona.role}.
        Your interests are: {', '.join(self.persona.interests)}.
        Your tone is: {self.persona.tone}.
        
        Analyze the provided news article and explain why it matters to you specifically.
        Be brief, insightful, and strategic.
        If an article is completely irrelevant to your persona, give it a relevance_score of 0.
        """
        
    def analyze_article(self, article_title: str, article_summary: str) -> Optional[Insight]:
        """Analyze a single article using the chosen LLM via LiteLLM."""
        
        # Check if any relevant API key is present for the chosen provider
        provider = config.ai.provider.lower()
        key_env_map = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GOOGLE_API_KEY"}
        
        # Mock mode if no key (so user can see UI work)
        if not os.getenv(key_env_map.get(provider, "")):
            import random
            mock_insights = [
                Insight(
                    why_it_matters="This article shows a clear trend in AI agent autonomy.",
                    actionable_insight="Review the repo linked in the article for architectural patterns.",
                    relevance_score=random.randint(4, 9)
                ),
                Insight(
                    why_it_matters="A strategic shift for distributed systems architecture.",
                    actionable_insight="Consider how this applies to our current multi-agent scaling problems.",
                    relevance_score=random.randint(3, 8)
                )
            ]
            return random.choice(mock_insights)

        user_content = f"Title: {article_title}\n\nSummary: {article_summary}"
        
        try:
            # Using LiteLLM's structured output capability
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=500,
                temperature=config.ai.temperature,
                response_format=Insight
            )
            
            # Simple manual parse if the response_format isn't supported by the specific model
            # but LiteLLM handles this for most major providers
            import json
            content = response.choices[0].message.content
            return Insight.model_validate_json(content)
            
        except Exception as e:
            logging.error(f"Error in AI analysis: {e}")
            return None
