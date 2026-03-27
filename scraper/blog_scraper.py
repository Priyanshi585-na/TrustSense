import trafilatura
from bs4 import BeautifulSoup
import json
from utils.tagging import tagging
from utils.chunking import chunking
from langdetect import detect
from urllib.parse import urlparse


blog_urls = ["https://jamesclear.com/3-2-1/march-5-2026","https://krebsonsecurity.com/2026/03/canisterworm-springs-wiper-attack-targeting-iran/","https://www.jansatta.com/photos/picture-gallery/world-richest-countries-powered-by-natural-resources/4461414/"]


months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

for url in blog_urls:
    article = trafilatura.fetch_url(url)
    result = trafilatura.extract(article,output_format = 'json',with_metadata=True, include_comments=False)
    result = json.loads(result)

    author = result['author']

    if author != None: 
        author_tokens = [token for token in author.split() if token not in months and not token.isnumeric()]
        author = " ".join(author_tokens)
    
    else:
        soup = BeautifulSoup(article, 'html.parser')
        try:
            author_twitter = soup.find('meta', attrs={'name': 'twitter:site'})['content']
            author = author_twitter.replace('@','')
        except:
            author = 'Anonymous'
        


    title = result['title']
    published_date = result['date']

    raw_text = result['raw_text']
    language = detect(raw_text)

    domain = urlparse(url).netloc
    if domain.endswith((".in",".us","uk",".ir")):
        region = domain[:-3].replace('.','').toupper()
    else:
        region = 'Unknown'

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
    


