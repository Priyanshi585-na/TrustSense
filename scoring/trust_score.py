import requests
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

class TrustScore:
    
    data = {}

    def __init__(self, data):
        self.data = data
        

    def affiliation_score(self):
        if self.data['source_type'] == 'pubmed':
            affiliations = self.data['affiliations']
            try:
                scores = []
                for aff in set(affiliations):
                    url = "https://api.openalex.org/institutions?search="
                    response = requests.get(f"{url}{aff}").json()

                    works_count = response['results'][0]['works_count']
                    citation = response['results'][0]['cited_by_count']
                    score = 0.5*np.log1p(works_count) + 0.5*np.log1p(citation)
                    scores.append(score)

                scores = np.array(scores)
                avg_score = (np.mean(scores)) 
                MAX_LOG = 15 
                norm_score = min(avg_score / MAX_LOG, 1)

                return norm_score
            
            except:
                return 0.3


    def author_credibility(self):
        if self.data['source_type'] == 'pubmed':
            authors = self.data['author']
            authors = authors.split(',')  
            affiliations = self.data['affiliations']

            scores = []
            for author, aff in zip(authors, affiliations):
                try:
                    inst_res = requests.get(f"https://api.openalex.org/institutions?search={aff}").json()

                    inst_id = inst_res["results"][0]["id"]
                    res = requests.get(f"https://api.openalex.org/authors?search={author}&filter=last_known_institutions.id:{inst_id}").json()


                    author = res["results"][0]

                    works_count = author.get("works_count", 0)
                    cite_count = author.get("cited_by_count", 0)
                    try:
                        h_index = author['summary_stats']['h_index']
                    except:
                        h_index = 0

                    score = 0.3*np.log1p(works_count) + 0.5*np.log1p(cite_count) + 0.2*np.log1p(h_index)
                    scores.append(score)

                except:
                    continue

            if not scores:
                return self.affiliation_score()

            avg_score = np.mean(scores)
            author_score = float(min(avg_score / 15, 1))
            aff_score = self.affiliation_score()
            return 0.3*aff_score + 0.7*author_score
        
        elif self.data['source_type'] == 'youtube':
            subs = np.log1p(self.data['subscribers'])
            return min(subs / 15, 1)
        

            

    def citation_count(self):
        if (self.data['source_type'] == 'pubmed'):
            try:
                pmid = self.data['pmid']
                res = requests.get(f"https://api.openalex.org/works?filter=ids.pmid:{pmid}").json()
                cites = res["results"][0].get("cited_by_count", 0)
                score = np.log1p(cites)
                return min(score / 10, 1)

            except:
                return 0.3
            
        elif self.data['source_type'] == 'youtube':
            likes =  np.log1p(self.data['likes'])
            views = np.log1p(self.data['views'])
            score = 0.7 * views + 0.3 * likes
            return min(score / 20, 1)       


    def recency(self):
        try:
            published_date = self.data['published_date']
            pub_year = datetime.strptime(published_date, '%Y-%m-%d').year
            years_old =  datetime.now().year - pub_year

            if years_old <= 3:
                return 1
            elif years_old <= 10:
                return 0.7
            elif years_old <= 15:
                return 0
            else:
                return -5
        except:
            return -10

    
    def medical_disclamer_presence(self):
        medical_phrases = ["not medical advice",
                            "consult a doctor",
                            "for informational purposes only",
                            "seek professional help",
                            "not a substitute for medical advice"]
        
        content_chunks = self.data['content_chunks']
        abstract = " ".join(content_chunks)
        for phrase in medical_phrases:
            if phrase in abstract:
                return 1
        return 0
        
    def domain_authority(self):
        url = self.data["source_url"]
        if '.gov' in url or '.org' in url:
            return 1
        else:
            try:
                domain = urlparse(url).netloc
                domain = domain.replace("www.", "")
                api_key = os.getenv('openpagerank_api')
                response = requests.get("https://openpagerank.com/api/v1.0/getPageRank", params={"domains[]": domain},headers={'API-OPR':api_key}).json()
                score = (response['response'][0]['page_rank_decimal'])/10
                return score
            
            except:
                return 0
            

    def trust_score(self):
        author_credibility = self.author_credibility()
        domain_authority = self.domain_authority()
        recency = self.recency()
        medical_disclamer_presence = self.medical_disclamer_presence()
        citation_count = self.citation_count()

        if self.data['source_type'] != 'blog':
            return 0.25*author_credibility + 0.25*domain_authority + 0.2*citation_count + 0.2*recency + 0.1*medical_disclamer_presence
        else:
            return 0.6*domain_authority + 0.3*recency + 0.1*medical_disclamer_presence    
        