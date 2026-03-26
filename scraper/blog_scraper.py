import trafilatura
import json
from utils.tagging import tagging
from utils.chunking import chunking
from langdetect import detect
from urllib.parse import urlparse


blog_urls = ["https://jamesclear.com/3-2-1/march-5-2026","https://krebsonsecurity.com/2026/03/canisterworm-springs-wiper-attack-targeting-iran/","https://hindialphabet.com/heart-beaking-love-stories"]


for url in blog_urls:

    article = trafilatura.fetch_url(url)
    result = trafilatura.extract(article,output_format = 'json',with_metadata=True, include_comments=False)
    result = json.loads(result)

    author = result['author']
    title = result['title']
    published_date = result['date']

    raw_text = result['raw_text']
    language = detect(raw_text)

    domain = urlparse(url).netloc
    if domain.endswith((".in",".us","uk",".ir")):
        region = domain[:-3].replace('.','').toupper()
    else:
        region = None

    topic_tags = tagging(raw_text)
    content_chunks = chunking(raw_text)

    
    print({ 
     "source_url": url, 
     "source_type": "blog", 
     "author": author, 
     "published_date": published_date, 
     "language": language, 
     "region": region, 
     "topic_tags": topic_tags, 
     "trust_score": "", 
     "content_chunks": content_chunks
     } )
    break;



"""   requests + BeautifulSoup — for scraping blog posts and PubMed (simple HTML parsing)
Selenium or Playwright — if blogs have JavaScript-rendered content
youtube-transcript-api — to pull YouTube transcripts without the YouTube API
google-api-python-client — for YouTube metadata (channel name, publish date, description)
Bio.Entrez (Biopython) — the standard library for fetching PubMed articles programmatically

Topic Tagging

KeyBERT — best choice; extracts meaningful keyword tags using BERT embeddings
spaCy — for NLP preprocessing (tokenization, NER) if you want lightweight tagging
langdetect — to auto-detect language of content

Trust Scoring

whois / requests to Moz/Ahrefs API — for domain authority (Moz has a free tier)
Plain Python logic is fine for the scoring formula — no special library needed
datetime — for recency calculation

Content Chunking

LangChain's RecursiveCharacterTextSplitter — cleanest option for splitting long text into chunks
Or simple manual splitting by paragraph using Python string operations

Data Storage

Python's built-in json module — sufficient for saving structured output
pandas — optional, useful if you want to inspect/export data as CSV too

Project Structure & Dev

python-dotenv — for storing API keys securely
logging module — for tracking scraping errors gracefully
     """