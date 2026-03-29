from Bio import Entrez
from dotenv import load_dotenv
import os
from utils.chunking import chunking
from utils.tagging import tagging
from scoring.trust_score import TrustScore

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
affiliations = []

for author in authors_list:
    first = author['ForeName']
    last = author['LastName']
    authors.append(f"{first} {last}")
    affiliations.append(author['AffiliationInfo'][0]['Affiliation'].split(',')[1])

author = ", ".join(authors) 

date = article["Journal"]["JournalIssue"]["PubDate"]
year  = date["Year"]
month = date["Month"]
day   = date["Day"]

published_date = f"{year}-{month}-{day}"

abstract = str(article['Abstract']['AbstractText'][0])
content_chunks = chunking(abstract)

language = str(article.get("Language"[0], "Unknown"))

try:
    region = records['PubmedArticle'][0]['MedlineCitation']['Country']
except:
    region = "Unknown"


try:
    keywords = records['PubmedArticle'][0]['MedlineCitation']['KeywordList']
    topic_tags = [str(k) for k in keywords[0]]
except:
    topic_tags = tagging(abstract)


data = { 
     "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", 
     "source_type": "pubmed", 
     "author": author, 
     "affiliations" : affiliations,
     "published_date": published_date, 
     "language": language, 
     "region": region, 
     "topic_tags": topic_tags, 
     "trust_score": "", 
     "content_chunks": content_chunks
     }

# print(data)

score = TrustScore(data)
a_score = score.author_credibility()
print(a_score)