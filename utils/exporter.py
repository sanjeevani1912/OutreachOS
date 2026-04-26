import json
import pandas as pd
import os
from datetime import datetime

class Exporter:
    @staticmethod
    def _ensure_dir(filename):
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def to_json(data, filename="data/enriched_creators.json"):
        Exporter._ensure_dir(filename)
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
            
    @staticmethod
    def to_csv(data, filename="data/outreach_export.csv"):
        Exporter._ensure_dir(filename)
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

    @staticmethod
    def save_run(data):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder = f"data/runs/{timestamp}"
        
        json_path = f"{folder}/creators.json"
        csv_path = f"{folder}/creators.csv"
        
        Exporter.to_json(data, json_path)
        
        # Format for CSV
        csv_data = []
        for d in data:
            csv_data.append({
                "Handle": d.get("creator_handle", d.get("handle", "")),
                "Platform": d.get("platform", ""),
                "Followers": d.get("followers", d.get("follower_count", 0)),
                "Engagement %": d.get("engagement_rate", 0),
                "Fit Score": d.get("brand_fit_score", 0),
                "Niche": d.get("niche", ""),
                "Quality": d.get("engagement_quality", ""),
                "Collab": d.get("collaboration_recommended", "")
            })
            
        Exporter.to_csv(csv_data, csv_path)
        return folder
