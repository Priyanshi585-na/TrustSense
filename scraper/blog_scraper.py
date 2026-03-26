from bs4 import BeautifulSoup
import requests
from newspaper import Article
import nltk
import trafilatura
import json

# nltk.download('punkt_tab')

blog_urls = ["https://jamesclear.com/3-2-1/march-5-2026","https://krebsonsecurity.com/2026/03/canisterworm-springs-wiper-attack-targeting-iran/","https://hindialphabet.com/heart-beaking-love-stories"]


for url in blog_urls:

    article = trafilatura.fetch_url(url)
    result = trafilatura.extract(article,output_format = 'json',with_metadata=True)
    result = json.loads(result)
    print(result['author'])
    print(result['title'])
    print(result['date'])


    # article = Article(url)
    # article.download()
    # article.parse()
    # article.html
    # print(article.authors)
    # article.nlp()
    # print(article.keywords)


    #  html = requests.get(url).text
    #  soup = BeautifulSoup(html, "html.parser")

    #  author = soup.find('div', class_ = 'post-info-author' ).find('a')
    #  date = soup.find('div', class_ = 'post-info-cat')
     
    #  { 
    #  "source_url": url, 
    #  "source_type": "blog", 
    #  "author": author.text, 
    #  "published_date": date.text.strip(), 
    #  "language": "", 
    #  "region": "", 
    #  "topic_tags": [], 
    #  "trust_score": "", 
    #  "content_chunks": [] 
    #  } 
     