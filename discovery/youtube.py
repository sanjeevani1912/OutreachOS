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

    def search_influencers(self, keyword, max_results=50):
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
                id=','.join(channel_ids), part='snippet,statistics'
            ).execute()

            influencers = []
            for item in channels_response['items']:
                stats = item['statistics']
                name = item['snippet']['title']
                if stats.get('hiddenSubscriberCount', False): continue
                
                subs = int(stats.get('subscriberCount', 0))
                print(f"    - {name}: {subs} subs")
                
                if MIN_FOLLOWERS <= subs <= MAX_FOLLOWERS:
                    description = item['snippet']['description']
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
                    contact_email = email_match.group(0) if email_match else "Not listed"
                    
                    influencers.append({
                        "platform": "YouTube",
                        "name": item['snippet']['title'],
                        "handle": item['snippet'].get('customUrl', item['snippet']['title']),
                        "follower_count": subs,
                        "profile_link": f"https://www.youtube.com/{item['snippet'].get('customUrl', 'channel/' + item['id'])}",
                        "profile_pic": item['snippet'].get('thumbnails', {}).get('default', {}).get('url', ''),
                        "description": description,
                        "recent_video": channel_video_map.get(item['id'], "No recent video found"),
                        "contact_email": contact_email,
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
