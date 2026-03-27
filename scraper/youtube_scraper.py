from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()

youtube_ids = ["oBklltKXtDE","UabBYexBD4k"]

for id in youtube_ids:
    transcript = ytt_api.fetch(id)
    text = " ".join(snippet.text.strip() for snippet in transcript)