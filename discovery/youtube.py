import os
import re
from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY, MIN_FOLLOWERS, MAX_FOLLOWERS

class YouTubeDiscovery:
    def __init__(self):
        self.youtube = None
        if YOUTUBE_API_KEY:
            try:
                self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            except Exception as e:
                print(f"[!] Failed to initialize YouTube client: {e}")

    def search_influencers(self, keyword, max_results=50, min_followers=1000, max_followers=100000):
        if not self.youtube:
            print("[!] YouTube API key missing or invalid. Skipping live discovery.")
            return []

        print(f"[*] Searching YouTube for: {keyword}...")
        try:
            search_response = self.youtube.search().list(
                q=keyword, part='snippet', type='video',
                maxResults=max_results, regionCode='IN', relevanceLanguage='en'
            ).execute()

            channel_video_map = {}
            for item in search_response['items']:
                cid = item['snippet']['channelId']
                if cid not in channel_video_map:
                    channel_video_map[cid] = item['snippet']['title']
                    
            channel_ids = list(channel_video_map.keys())
            if not channel_ids: return []

            print(f"[*] Found {len(channel_ids)} unique channels. Checking follower counts...")
            channels_response = self.youtube.channels().list(
                id=','.join(channel_ids), part='snippet,statistics,brandingSettings'
            ).execute()

            influencers = []
            for item in channels_response['items']:
                stats = item['statistics']
                name = item['snippet']['title']
                if stats.get('hiddenSubscriberCount', False): continue
                
                subs = int(stats.get('subscriberCount', 0))
                print(f"    - {name}: {subs} subs")
                
                if min_followers <= subs <= max_followers:
                    snippet = item['snippet']
                    description = snippet['description']
                    
                    # 1. Official Country from Metadata
                    country = snippet.get('country', 'India') # Default to India for this project if not set
                    
                    # 2. Email Extraction from Description
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
                    contact_email = email_match.group(0) if email_match else "Not listed"
                    
                    # 3. Instagram Handle Extraction (Regex on Description + Official Links)
                    ig_handle = "Not listed"
                    ig_patterns = [
                        r'instagram\.com/([a-zA-Z0-9._]+)',
                        r'ig:?\s*@?([a-zA-Z0-9._]+)',
                        r'insta:?\s*@?([a-zA-Z0-9._]+)'
                    ]
                    
                    # Check description first
                    for pattern in ig_patterns:
                        match = re.search(pattern, description, re.IGNORECASE)
                        if match:
                            ig_handle = f"@{match.group(1).strip('/')}"
                            break
                    
                    # Fallback to branding keywords or title if still missing
                    if ig_handle == "Not listed":
                        custom_url = snippet.get('customUrl', '')
                        if custom_url and custom_url.startswith('@'):
                            ig_handle = custom_url # Use custom URL as a proxy handle
                    
                    influencers.append({
                        "platform": "YouTube",
                        "name": snippet['title'],
                        "handle": ig_handle,
                        "follower_count": subs,
                        "profile_link": f"https://www.youtube.com/{snippet.get('customUrl', 'channel/' + item['id'])}",
                        "profile_pic": snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                        "description": description,
                        "recent_video": channel_video_map.get(item['id'], "No recent video found"),
                        "contact_email": contact_email,
                        "country": country,
                        "id": item['id'],
                        "metadata": {
                            "view_count": stats.get('viewCount'),
                            "video_count": stats.get('videoCount')
                        }
                    })
            
            print(f"[+] Found {len(influencers)} influencers matching criteria.")
            return influencers
        except Exception as e:
            print(f"[!] YouTube API Error: {e}")
            return []
