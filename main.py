import sys
import logging
from app.config import config
from app.feeds import aggregate_feeds
from app.agent import InsightAgent, AnalyzedArticle
from app.ui import display_welcome, display_briefing, display_insight_card, display_status, display_error
from app.notify import dispatch_briefing

def run_pulse():
    # 1. Start UI
    display_welcome()
    
    # 2. Fetch Feeds
    display_status("Syncing with global feeds...")
    raw_articles = aggregate_feeds(config.feeds)
    
    if not raw_articles:
        display_error("No articles found. Check your Internet connection or feed URLs.")
        return
        
    display_status(f"Found {len(raw_articles)} recent stories. Starting Agentic analysis...")
    
    # 3. Analyze with Agent
    agent = InsightAgent()
    analyzed_results = []
    
    # Process only the first 10 articles to stay within reasonable time/token limits
    # You can increase this in the future!
    for article in raw_articles[:12]:
        display_status(f"Analyzing: {article.title[:50]}...")
        insight = agent.analyze_article(article.title, article.summary)
        
        if insight:
            analyzed_results.append(AnalyzedArticle(
                title=article.title,
                link=article.link,
                source=article.source,
                insight=insight
            ))
            
    if not analyzed_results:
        display_error("AI Agent could not process any articles. Check your API keys in .env.")
        return

    # 4. Display Results
    display_briefing(analyzed_results)
    
    # Show detailed cards for the best ones
    for result in analyzed_results:
        display_insight_card(result)
        
    # 5. Notify Mobile
    display_status("Dispatching briefing to your iPhone...")
    dispatch_briefing(analyzed_results)
    
    display_status("Pulse Check Complete. See you tomorrow!")

if __name__ == "__main__":
    try:
        run_pulse()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(0)
    except Exception as e:
        display_error(f"Unexpected crash: {e}")
        sys.exit(1)
