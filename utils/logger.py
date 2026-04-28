from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.rule import Rule
import os

# Force UTF-8 on Windows terminals to support box-drawing characters
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
console = Console(highlight=False)

def print_banner(keyword, brand_name, target_count):
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]OutreachOS[/bold cyan]  [dim]|[/dim]  Influencer Intelligence Platform\n"
        f"[dim]Keyword:[/dim] [bold white]{keyword}[/bold white]   "
        f"[dim]Brand:[/dim] [bold white]{brand_name}[/bold white]   "
        f"[dim]Target:[/dim] [bold white]{target_count} creators[/bold white]",
        border_style="cyan",
        padding=(1, 4)
    ))
    console.print()

def print_step(step_num, total_steps, label, detail=""):
    steps = ["●", "●", "●", "●", "●"]
    bar = ""
    for i in range(total_steps):
        if i < step_num:
            bar += "[green]●[/green] "
        elif i == step_num:
            bar += "[bold cyan]●[/bold cyan] "
        else:
            bar += "[dim]○[/dim] "
    console.print(f"  {bar}  [bold]{label}[/bold]" + (f"  [dim]{detail}[/dim]" if detail else ""))

def print_discovery_results(influencers, platform="YouTube"):
    console.print()
    console.print(Rule(f"[bold cyan] Discovery — {platform} [/bold cyan]", style="cyan"))
    
    if not influencers:
        console.print("  [yellow]⚠  No influencers matched the criteria.[/yellow]")
        return

    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True, header_style="bold white on #1a3a4a")
    table.add_column("Creator", style="bold white", min_width=22)
    table.add_column("Subscribers", justify="right", style="cyan")
    table.add_column("Handle", style="dim")
    table.add_column("Status", justify="center")

    for inf in influencers:
        subs = inf.get('follower_count', 0)
        subs_fmt = f"{subs/1000:.1f}K" if subs < 1_000_000 else f"{subs/1_000_000:.1f}M"
        status = "[green]OK[/green]"
        table.add_row(inf.get('name', ''), subs_fmt, inf.get('handle', ''), status)

    console.print(table)
    console.print(f"  [green]✓[/green] [bold]{len(influencers)} creator(s)[/bold] matched the follower range filter.\n")

def print_analysis_result(creator, analysis):
    niche     = analysis.get('niche', '—')
    score     = analysis.get('relevance_score', '—')
    reasoning = analysis.get('reasoning', '')
    themes    = ', '.join(analysis.get('content_themes', []))
    signals   = ', '.join(analysis.get('recent_signals', []))

    score_color = "green" if score != '—' and int(score) >= 70 else ("yellow" if score != '—' and int(score) >= 50 else "red")
    
    console.print(Panel(
        f"[dim]Niche:[/dim]     [bold white]{niche}[/bold white]\n"
        f"[dim]Fit Score:[/dim] [{score_color}][bold]{score}/100[/bold][/{score_color}]\n"
        f"[dim]Themes:[/dim]    [white]{themes}[/white]\n"
        f"[dim]Signals:[/dim]   [white]{signals}[/white]\n"
        f"[dim]Reasoning:[/dim] [italic]{reasoning[:120]}...[/italic]" if len(reasoning) > 120 else f"[dim]Reasoning:[/dim] [italic]{reasoning}[/italic]",
        title=f"[bold cyan]⚡ AI Analysis — {creator}[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))

def print_outreach_preview(creator, outreach_data):
    prof_data = outreach_data.get('professional', outreach_data)
    email = prof_data.get('email', '')
    dm    = prof_data.get('dm', '')
    
    preview = email[:300] + "..." if len(email) > 300 else email
    console.print(Panel(
        f"[dim]EMAIL:[/dim]\n[white]{preview}[/white]\n\n"
        f"[dim]DM:[/dim]\n[white]{dm}[/white]",
        title=f"[bold cyan]✉  Outreach Generated — {creator}[/bold cyan]",
        border_style="cyan",
        padding=(0, 2)
    ))

def print_summary_table(results):
    console.print()
    console.print(Rule("[bold cyan] Pipeline Complete [/bold cyan]", style="cyan"))
    console.print()

    table = Table(box=box.ROUNDED, border_style="green", show_header=True, header_style="bold white on dark_green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Creator", style="bold white", min_width=22)
    table.add_column("Platform", justify="center")
    table.add_column("Followers", justify="right", style="cyan")
    table.add_column("Eng. Rate", justify="right", style="magenta")
    table.add_column("Niche", style="white")
    table.add_column("Fit Score", justify="center")
    table.add_column("Collab Type", style="dim")

    for i, r in enumerate(results, 1):
        score = r.get('brand_fit_score', r.get('adjusted_brand_fit_score', '—'))
        subs  = r.get('follower_count', 0)
        eng   = r.get('engagement_rate', 0)
        subs_fmt = f"{subs/1000:.1f}K" if subs < 1_000_000 else f"{subs/1_000_000:.1f}M"
        score_str = f"[green]{score}%[/green]" if isinstance(score, int) and score >= 70 else \
                    (f"[yellow]{score}%[/yellow]" if isinstance(score, int) and score >= 50 else f"[red]{score}%[/red]")
        table.add_row(
            str(i),
            r.get('name', ''),
            r.get('platform', ''),
            subs_fmt,
            f"{eng}%",
            r.get('niche', '—'),
            score_str,
            r.get('recommended_collab_type', r.get('collaboration_recommended', '—'))
        )

    console.print(table)
    console.print()

def print_save_confirmation(path):
    console.print(Panel(
        f"[green]OK[/green] Full enriched report saved to: [bold cyan]{path}[/bold cyan]\n"
        f"[dim]Open it to inspect AI analysis, scores, and generated outreach messages.[/dim]",
        border_style="green",
        padding=(0, 2)
    ))
    console.print()
