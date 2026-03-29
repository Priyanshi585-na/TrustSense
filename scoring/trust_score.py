import requests
import numpy as np
from functools import lru_cache


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
        else:
            pass


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

                    score = 0.3*np.log1p(works_count) + 0.7*np.log1p(cite_count)
                    scores.append(score)

                except:
                    continue

            if not scores:
                return self.affiliation_score

            avg_score = np.mean(scores)
            author_score = float(min(avg_score / 15, 1))
            aff_score = self.affiliation_score()
            return 0.3*aff_score + 0.7*author_score