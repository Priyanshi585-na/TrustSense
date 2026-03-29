from youtube_transcript_api import YouTubeTranscriptApi
from utils.tagging import tagging
from utils.chunking import chunking
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import json
from concurrent.futures import ThreadPoolExecutor
from scoring.trust_score import TrustScore


load_dotenv()
ytt_api = YouTubeTranscriptApi()
api_key = os.getenv('key')
youtube = build("youtube", "v3", developerKey=api_key)

channel_ids = []
data = []


def process_video(youtube_response):
    for item in youtube_response['items']:
        results = {}
        vid_id = item['id']
        results["source_url"] = f"https://www.youtube.com/watch?v={vid_id}"
        results["source_type"] = "youtube"
        results["author"] = item['snippet']['channelTitle']
        results["published_date"] = item['snippet']['publishedAt'].split('T')[0]
        channel_ids.append(item["snippet"]["channelId"])
        results['channel_id'] = item['snippet']['channelId']
        results["language"] = item['snippet'].get('defaultAudioLanguage', "Unknown")

        stats = item["statistics"]

        results["views"] = int(stats.get("viewCount", 0))
        results["likes"] = int(stats.get("likeCount", 0))

        text = transcript_map.get(vid_id, "")

        if(item['snippet'].get('tags')):
            results["topic_tags"] = item['snippet']['tags']
        else:
            results["topic_tags"] = tagging(text)

        results["content_chunks"] = chunking(text)

        data.append(results)


def process_channel(cids):
    response = youtube.channels().list(part="snippet,statistics", id=cids).execute()

    channel_map = {}

    for item in response['items']:
        cid = item['id']

        channel_map[cid] = {
            "region": item['snippet'].get('country', "Unknown"),
            "subscribers": int(item["statistics"].get("subscriberCount", 0))
        }

    for i in range(len(data)):
        cid = data[i]["channel_id"]

        data[i]["region"] = channel_map.get(cid, {}).get("region", "Unknown")
        data[i]["subscribers"] = channel_map.get(cid, {}).get("subscribers", 0)

        data[i].pop("channel_id")



def fetch_transcript(vid_id):
        try:
            transcript = ytt_api.fetch(vid_id)
            text = " ".join(s.text.strip() for s in transcript)
            return text
        except:
             return ""

youtube_ids = ["oBklltKXtDE","UabBYexBD4k"]

with ThreadPoolExecutor(max_workers=3) as executor:
     transcripts = list(executor.map(fetch_transcript, youtube_ids))

transcript_map = dict(zip(youtube_ids, transcripts))


ids = ",".join(youtube_ids)
youtube_response = youtube.videos().list(part = "snippet,statistics", id = ids).execute()

process_video(youtube_response)

cids = ",".join(channel_ids)
process_channel(cids)

for d in data:   
    trustscore = TrustScore(d)
    score = trustscore.trust_score()
    d['trust_score'] = score
    d.pop('likes')
    d.pop('views')
    d.pop('subscribers')


with open('output/scraped_data.json','r', encoding='utf-8') as file:
     all_data = json.load(file)

all_data.extend(data)
with open('output/scraped_data.json','w', encoding='utf-8') as file:
     json.dump(all_data,file, indent=4, ensure_ascii=False)
