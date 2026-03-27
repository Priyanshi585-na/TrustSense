from youtube_transcript_api import YouTubeTranscriptApi
from utils.tagging import tagging
from utils.chunking import chunking
from dotenv import load_dotenv
from googleapiclient.discovery import build
import os


load_dotenv()
ytt_api = YouTubeTranscriptApi()
api_key = os.getenv('key')
youtube = build("youtube", "v3", developerKey=api_key)

youtube_ids = ["oBklltKXtDE","UabBYexBD4k"]

for id in youtube_ids:
    transcript = ytt_api.fetch(id)
    text = " ".join(snippet.text.strip() for snippet in transcript)

    response = youtube.videos().list(part="snippet", id = id).execute()
    published_date = response['items'][0]['snippet']['publishedAt'].split('T')[0]
    author = response['items'][0]['snippet']['channelTitle']

    channel_id = response['items'][0]["snippet"]["channelId"]

    language = transcript.language_code

    channel_response = youtube.channels().list(part = 'snippet', id = channel_id).execute()
    try:
       region = channel_response['items'][0]['snippet']['country']

    except:
        region = None

    topic_tags = tagging(text)
    content_chunks = chunking(text)

    
    print({ 
     "source_url": f"https://www.youtube.com/watch?v={id}", 
     "source_type": "youtube", 
     "author": author, 
     "published_date": published_date, 
     "language": language, 
     "region": region, 
     "topic_tags": topic_tags, 
     "trust_score": "", 
     "content_chunks": content_chunks
     } )