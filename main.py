import sys
import os
import time

from discovery.youtube import YouTubeDiscovery
from discovery.instagram import InstagramDiscovery
from intelligence.analyzer import ContentAnalyzer
from intelligence.scorer import BrandFitScorer
from intelligence.outreach import OutreachGenerator
from utils.exporter import Exporter
from utils.logger import (
    console, print_banner, print_step,
    print_discovery_results, print_analysis_result,
    print_outreach_preview, print_summary_table, print_save_confirmation
)
from config import BRAND_CONTEXT

TOTAL_STEPS = 5

def check_setup():
    from dotenv import load_dotenv
    load_dotenv()
    if not os.getenv("YOUTUBE_API_KEY") or not os.getenv("GEMINI_API_KEY"):
        console.print("[red][!!] Missing API keys. Check your .env file.[/red]")
        return False
    console.print("[green][OK] Environment loaded. API keys verified.[/green]")
    return True

def run_pipeline(keyword, target_count=5, brand_name=None, industry=None):
    if not check_setup(): return

    brand = brand_name or BRAND_CONTEXT['name']
    ind = industry or "General"
    print_banner(keyword, brand, target_count)

    # ─── STEP 1: Discovery ────────────────────────────────────────────────
    print_step(0, TOTAL_STEPS, "Discovery", "Searching YouTube & Instagram...")
    yt_engine = YouTubeDiscovery()
    ig_engine = InstagramDiscovery()

    yt_influencers = yt_engine.search_influencers(keyword, max_results=50)
    ig_influencers = ig_engine.search_influencers(keyword)

    print_discovery_results(yt_influencers, platform="YouTube")
    if ig_influencers:
        print_discovery_results(ig_influencers, platform="Instagram")

    all_influencers = (yt_influencers + ig_influencers)[:target_count]

    if not all_influencers:
        console.print("[red]✗  No influencers found matching criteria. Try a different keyword.[/red]")
        return

    # ─── STEP 2: Content Analysis ─────────────────────────────────────────
    print_step(1, TOTAL_STEPS, "Content Analysis", f"Running Gemini AI on {len(all_influencers)} creator(s)...")
    
    # Only use config brief if the brand name matches the config name
    if len(sys.argv) > 5:
        brief = sys.argv[5]
    elif brand == BRAND_CONTEXT.get('name'):
        brief = BRAND_CONTEXT.get('description', "No brief provided.")
    else:
        brief = f"a professional brand operating in the {ind} industry."
        
    analyzer = ContentAnalyzer(brand_name=brand, industry=ind, brand_brief=brief)
    for creator in all_influencers:
        try:
            analyzer.analyze(creator)
            print_analysis_result(creator['name'], creator)
        except Exception as e:
            if any(code in str(e) for code in ["404", "429", "503", "500"]):
                time.sleep(2) # Backoff before trying next model
                continue
            print(f"[!] Gemini Analysis Error: {e}")
            break

    # ─── STEP 3: Brand-Fit Scoring ────────────────────────────────────────
    print_step(2, TOTAL_STEPS, "Brand-Fit Scoring", "Applying algorithmic scoring rules...")
    scorer = BrandFitScorer()
    for creator in all_influencers:
        scorer.calculate_score(creator)

    # ─── STEP 4: Outreach Generation ─────────────────────────────────────
    print_step(3, TOTAL_STEPS, "Outreach Generation", f"Generating Professional & Friendly templates...")
    time.sleep(2)
    outreach_gen = OutreachGenerator(brand_name=brand, industry=ind, brand_brief=brief)
    for creator in all_influencers:
        outreach_gen.generate(creator)
        if creator.get('outreach'):
            print_outreach_preview(creator['name'], creator['outreach'])

    # ─── STEP 5: Export ───────────────────────────────────────────────────
    print_step(4, TOTAL_STEPS, "Persistence", "Exporting pipeline results...")
    saved_folder = Exporter.save_run(all_influencers)
    console.print(f"[green]✓ Successfully exported pipeline run to {saved_folder}[/green]")

    # ─── Summary Table ────────────────────────────────────────────────────
    print_summary_table(all_influencers)

if __name__ == "__main__":
    kw    = sys.argv[1] if len(sys.argv) > 1 else "skincare India"
    brand = sys.argv[2] if len(sys.argv) > 2 else "HelloWorld"
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    ind   = sys.argv[4] if len(sys.argv) > 4 else "General"
    run_pipeline(kw, count, brand_name=brand, industry=ind)
