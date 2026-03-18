from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress
from rich.style import Style
from rich import box
from datetime import datetime
from .config import config

console = Console()

def display_welcome():
    title = Text("InsightPulse v1.0", style="bold cyan")
    subtitle = Text(f"Connected as: {config.persona.name} | {config.persona.role}", style="italic dim white")
    console.print(Panel(title + "\n" + subtitle, box=box.HEAVY, border_style="bright_blue"))
    console.print("\n")

def display_briefing(analyzed_articles):
    """
    Shows a summary table of all fetched articles.
    """
    table = Table(title=f"Daily Pulse Briefing - {datetime.now().strftime('%Y-%m-%d')}", box=box.ROUNDED)
    table.add_column("Score", justify="center", style="green", width=6)
    table.add_column("Article Title", style="bold white")
    table.add_column("Source", style="cyan", width=15)
    
    # Sort by relevance to show the best insights first
    sorted_articles = sorted(analyzed_articles, key=lambda x: x.insight.relevance_score, reverse=True)
    
    for article in sorted_articles:
        score = article.insight.relevance_score
        color = "green" if score >= 8 else "yellow" if score >= 5 else "red"
        table.add_row(
            f"[{color}]{score}[/]",
            article.title,
            article.source
        )
    
    console.print(table)
    console.print("\n")

def display_insight_card(article):
    """
    Shows a detailed 'Insight Card' for high-relevance articles.
    """
    if article.insight.relevance_score < 4:
        return # Don't show cards for low-value stuff

    console.print(Panel(
        f"[bold white]{article.title}[/]\n"
        f"[dim cyan]Source:[/] {article.source}\n\n"
        f"[bold yellow]THE 'WHY':[/]\n{article.insight.why_it_matters}\n\n"
        f"[bold green]NEXT ACTION:[/]\n{article.insight.actionable_insight}",
        title=f"Insight Score: {article.insight.relevance_score}/10",
        border_style="bright_magenta" if article.insight.relevance_score >= 8 else "blue",
        width=80
    ))
    console.print("\n")

def display_error(msg):
    console.print(f"[bold red]ERROR:[/] {msg}")

def display_status(msg):
    console.print(f"[dim white]>>> {msg}[/]")
