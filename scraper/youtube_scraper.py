from youtube_transcript_api import YouTubeTranscriptApi
from utils.tagging import tagging
from utils.chunking import chunking
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
from concurrent.futures import ThreadPoolExecutor


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

        text = transcript_map.get(vid_id, "")

        if(item['snippet']['tags']):
            results["topic_tags"] = item['snippet']['tags']
        else:
            results["topic_tags"] = tagging(text)

        results["content_chunks"] = chunking(text)

        data.append(results)


def process_channel(cids):
    response = youtube.channels().list(part = "snippet", id = cids).execute()
    channel_map = {}
    for item in response['items']:
          channel_map[item['id']] = item['snippet'].get('country', "Unknown")
            
    for i in range(len(data)):
        cid = data[i]["channel_id"]
        data[i]["region"] = channel_map.get(cid, "Unknown")
        data[i].pop("channel_id")



def fetch_transcript(vid_id):
        transcript = ytt_api.fetch(vid_id)
        text = " ".join(s.text.strip() for s in transcript)
        return text


youtube_ids = ["oBklltKXtDE","UabBYexBD4k"]

with ThreadPoolExecutor(max_workers=3) as executor:
     transcripts = list(executor.map(fetch_transcript, youtube_ids))

transcript_map = dict(zip(youtube_ids, transcripts))


ids = ",".join(youtube_ids)
youtube_response = youtube.videos().list(part = "snippet", id = ids).execute()

process_video(youtube_response)

cids = ",".join(channel_ids)
process_channel(cids)

print(data)

