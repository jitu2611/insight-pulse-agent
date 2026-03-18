import feedparser
import httpx
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Article(BaseModel):
    title: str
    link: str
    summary: str = ""
    source: str = ""
    published: str = ""

def fetch_rss_feed(feed_url: str, feed_name: str = "Unknown Source") -> List[Article]:
    """Fetch and parse an RSS feed."""
    logger.info(f"Fetching: {feed_name} ({feed_url})")
    try:
        # Use feedparser directly, it's very robust
        feed = feedparser.parse(feed_url)
        articles = []
        
        # Limit to top 5 articles per feed for efficiency
        for entry in feed.entries[:5]:
            # Basic sanitization of HTML in summaries
            summary = entry.get('summary', entry.get('description', ''))
            # Simple HTML tag removal (naive but fast)
            import re
            summary = re.sub('<[^<]+?>', '', summary)[:300] # Max 300 chars
            
            articles.append(Article(
                title=entry.get('title', 'No Title'),
                link=entry.get('link', ''),
                summary=summary,
                source=feed_name,
                published=entry.get('published', '')
            ))
        return articles
    except Exception as e:
        logger.error(f"Error fetching {feed_url}: {e}")
        return []

def aggregate_feeds(feeds: List[Dict[str, str]]) -> List[Article]:
    """Aggregate all articles from a list of feeds."""
    all_articles = []
    for f in feeds:
        url = f.get('url')
        name = f.get('name', 'General')
        all_articles.extend(fetch_rss_feed(url, name))
    return all_articles
