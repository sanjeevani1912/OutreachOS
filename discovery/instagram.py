class InstagramDiscovery:
    def __init__(self):
        pass

    def search_influencers(self, keyword, max_results=5):
        print(f"[*] Searching Instagram for: {keyword} (via Adapter)...")
        # Generating a realistic dummy profile for UI demo purposes
        base_word = keyword.split(',')[0].split()[0].lower() if keyword else "lifestyle"
        return [
            {
                "platform": "Instagram",
                "name": f"The {base_word.capitalize()} Diary",
                "handle": f"@{base_word}_journey",
                "follower_count": 48500,
                "profile_link": f"https://instagram.com/{base_word}_journey",
                "description": f"Daily inspiration for {keyword}. 📍 India | Creating authentic content for a better lifestyle.",
                "id": "ig_mock_1",
                "metadata": {
                    "view_count": 1250000,
                    "video_count": 120
                }
            }
        ]
