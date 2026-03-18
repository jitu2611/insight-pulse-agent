import httpx
import logging
from typing import List
from .config import config

logger = logging.getLogger(__name__)

def send_ntfy_notification(title: str, message: str, priority: str = "default"):
    """
    Send a simplified notification via ntfy.sh (works great on iOS).
    You just need to install the 'ntfy' app and subscribe to the topic.
    """
    if not config.notifications.enabled:
        return
        
    topic = config.notifications.ntfy_topic
    url = f"https://ntfy.sh/{topic}"
    
    # Priority can be: 1 (min), 2 (low), 3 (default), 4 (high), 5 (max)
    # ntfy supports these as words too
    
    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": "newspaper,brain,rocket"
    }
    
    try:
        response = httpx.post(url, content=message, headers=headers)
        if response.status_code == 200:
            logger.info(f"Notification sent to ntfy.sh topic: {topic}")
        else:
            logger.error(f"Failed to send notification. HTTP {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending ntfy notification: {e}")

def dispatch_briefing(analyzed_articles):
    """
    Formats and sends the top 3 insights to the phone.
    """
    if not config.notifications.enabled:
        return
        
    # Sort by relevance
    sorted_articles = [a for a in analyzed_articles if a.insight.relevance_score >= 5]
    sorted_articles = sorted(sorted_articles, key=lambda x: x.insight.relevance_score, reverse=True)
    
    if not sorted_articles:
        send_ntfy_notification("Pulse Update", "No high-relevance news found today.", "low")
        return
        
    # Pick top 3
    top_3 = sorted_articles[:3]
    
    # Format the message for a small screen
    briefing = "Top Insights Today:\n\n"
    for i, article in enumerate(top_3):
        score = article.insight.relevance_score
        briefing += f"[{score}/10] {article.title}\n"
        briefing += f"Source: {article.source}\n\n"
    
    send_ntfy_notification(
        title=f"Daily Pulse: {len(sorted_articles)} New Insights",
        message=briefing,
        priority="high" if any(a.insight.relevance_score >= 8 for a in top_3) else "default"
    )
