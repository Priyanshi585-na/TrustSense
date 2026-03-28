from Bio import Entrez
from dotenv import load_dotenv
import os
from utils.chunking import chunking

load_dotenv()
email = os.getenv("email")
Entrez.email = email

pmid = "40001682"

response = Entrez.efetch(
    db="pubmed",
    id = pmid,
    retmode = "xml"
)

records = Entrez.read(response)

article = records['PubmedArticle'][0]['MedlineCitation']['Article']

authors_list = article['AuthorList']
authors = []

for author in authors_list:
    first = author['ForeName']
    last = author['LastName']
    authors.append(f"{first} {last}")

author = ", ".join(authors) 

date = article["Journal"]["JournalIssue"]["PubDate"]
year  = date["Year"]
month = date["Month"]
day   = date["Day"]

published_date = f"{year}-{month}-{day}"

abstract = str(article['Abstract']['AbstractText'][0])
content_chunks = chunking(abstract)

language = str(article["Language"][0])

try:
    region = records['PubmedArticle'][0]['MedlineCitation']['Country']
except:
    region = "Unknown"


keywords = records['PubmedArticle'][0]['MedlineCitation']['KeywordList']
topic_tags = [str(k) for k in keywords[0]]


print({ 
     "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", 
     "source_type": "pubmed", 
     "author": author, 
     "published_date": published_date, 
     "language": language, 
     "region": region, 
     "topic_tags": topic_tags, 
     "trust_score": "", 
     "content_chunks": content_chunks
     } )