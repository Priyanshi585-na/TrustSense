# TrustSense - Score the trust of everything you read/see
## Overview
TrustSense is a multi-sourced data scraper combined with the rule-based trust scoring system. It extracts structured data from heterogenous sources(blogs, YouTube and Pubmed) and evaluates their credibility using a unified scoring framework.
The core idea is to normalize different types of signals across platforms and compute a trust score between 0 and 1.

## Features
- Scrapes data from
  - Blogs
  - Youtube videos
  - Pubmed articles
- Extracts structured metadata
- Performs automatic topic tagging
- Splits content into chunks
- Compute a trust score based on multiple credibility factors
- Handles multilingual support
- Stores results in clear JSON format

## Tools and Libraries used
- Python
- requests
- trafilatura
- BeautifulSoup
- youtube-transcript-api
- Youtube Data API v3
- OpenAlex API
- OpenPageRank API
- langdetect
- BioPython(Entrez)
- langchain_text_splitters
- keyBERT

## Scraping approach
The system follows a source-specific scraping strategy, since each platform provides different structures, APIs and levels of data accessibility.

### 1. Blog Scraping

Blog content is highly unstructured and varies across websites, so a hybrid approach was used:

- Trafilatura
  - To extract clean article text, metadata and remove noise such as ads, navs and scripts.
  - **Fallback Parsing**:
    When metadata was missing, **BeautifulSoup** was used to extract information from HTML meta tags
  - **Processing Steps**
    - Extract raw article text
    - Detect language using langdetect
    - Infer region from domains
    - Generate topic tags using keyBERT
    - Split the content into chunks

### 2. Youtube Scraping

Youtube provided structured data via APIs, so an API-driven approach was used:

- **Metadata Extraction**
  Used the Youtube Data API v3 to fetch:
  - Channel Name (author)
  - Publish date
  - Video Statistics (views, likes)
  - Channel statistics (subscribers)
  - Language
  - Keywords
- **Transcript Extraction:**
  Used youtube-transcript-api to fetch video transcripts for chunking and tagging (if keywords are unavailable).
- **Processing Steps:**
  - Extract transcript and clean text
  - Generate topic tags
  - Chunk transcripts
 
### 3. PubMed Article Scraping
  Used the BioPython(Entrez) to fetch:
  - Title
  - Authors
  - Affiliations
  - Publish Date
  - Language
  - Keywords
  - Abstract (used for chunking)
- **Processing Steps:**
  - Parse XML response to structured data
  - Extract abstract and chunk into sections
  - Generate topic tags from KeywordList or KeyBERT fallback
 
## Trust Score Design

TrustSense evaluates each source using a weighted scoring model that returns a normalized score between 0 and 1. The scoring logic is source-type aware — blogs, YouTube videos and PubMed articles are scored differently based on what signals are available for each platform.

### Formula

**PubMed and YouTube:**
```
trust_score = 0.25 × author_credibility
            + 0.25 × domain_authority
            + 0.20 × citation_count
            + 0.20 × recency
            + 0.10 × medical_disclaimer_presence
```

**Blogs:**
```
trust_score = 0.60 × domain_authority
            + 0.30 × recency
            + 0.10 × medical_disclaimer_presence
```

> Blogs receive a simplified formula since author and citation data is largely unavailable or unreliable for arbitrary blog URLs.

---

### Signal Breakdown

#### 1. Author Credibility
- **PubMed:**
  Each author is looked up on the OpenAlex API using their name and institutional affiliation. Three signals are combined:
  - `works_count` — number of published works
  - `cited_by_count` — total citations received
  - `h_index` — research impact index
```
  author_score = 0.3×log(works) + 0.5×log(citations) + 0.2×log(h_index)
```

  If an author cannot be resolved, the affiliation score is used as a
  fallback. The final score combines both:
```
  final = 0.7×author_score + 0.3×affiliation_score
```

- **YouTube:**
  Scored using the channel's subscriber count:
```
  score = log(subscribers) / 15, capped at 1
```

- **Blogs:** Not scored — author data is unreliable for arbitrary URLs.

---

#### 2. Citation Count
- **PubMed:** Fetched from OpenAlex using the PubMed ID (PMID):
```
  score = log(cited_by_count) / 10, capped at 1
```

- **YouTube:** Approximated using video engagement signals:
```
  score = (0.7×log(views) + 0.3×log(likes)) / 20, capped at 1
```

- **Blogs:** Not scored — reliable citation data unavailable.

---

#### 3. Domain Authority
- URLs ending in `.gov` or `.org` receive a score of 1.0 automatically.
- All other domains are queried against the **OpenPageRank API**, which
  returns a score from 0–10, normalized to 0–1.
- Falls back to 0 if the API call fails.

---

#### 4. Recency
Scored based on the age of the content in years:

| Age          | Score |
|--------------|-------|
| ≤ 3 years    | 1.0   |
| ≤ 10 years   | 0.7   |
| ≤ 15 years   | 0.0   |
| > 15 years   | -5    |

Falls back to -10 if the publish date is missing or unparseable.

---

#### 5. Medical Disclaimer Presence
Scans the full content for phrases such as:
- "not medical advice"
- "consult a doctor"
- "for informational purposes only"
- "seek professional help"
- "not a substitute for medical advice"

Returns `1` if any phrase is found, `0` otherwise.

---

### Abuse Prevention

| Threat                    | Prevention                                              |
|---------------------------|---------------------------------------------------------|
| Fake authors              | Authors verified against OpenAlex institutional records |
| Low quality blogs         | OpenPageRank penalizes low authority domains            |
| Misleading medical content| Missing disclaimer returns 0 on that signal             |
| Outdated information      | Strong recency penalties for content older than 10 years|
| Unknown affiliations      | Falls back to affiliation-level score, not zero         |

---

## Limitations

- **Author credibility is PubMed and YouTube only.** Blog authors are not scored due to the lack of a reliable verification source for arbitrary web authors.

- **OpenAlex coverage is incomplete.** Lesser known authors or institutions may not appear in the API, causing fallback to affiliation score or 0.3 default.

- **Medical disclaimer detection is keyword-based.** Paraphrased disclaimers or disclaimers in non-English text will not be detected.

- **YouTube transcripts may be unavailable.** Auto-generated transcripts are used as fallback but may contain errors. Videos with no transcript at all result in empty content chunks.
  
- **No Adaptability.** Rule-based logic allows no learning and adaptability.
---

## How to Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/yourname/TrustSense.git
cd TrustSense
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory:
```
email=your@email.com
YOUTUBE_API_KEY=your_youtube_api_key
openpagerank_api=your_openpagerank_api_key
```

> - YouTube API key: https://console.cloud.google.com
> - OpenPageRank API key: https://www.domcop.com/openpagerank

### 5. Run the Scrapers

Run each scraper separately:
```bash
# Scrape blogs
python -m scraper.blog_scraper

# Scrape YouTube videos
python -m scraper.youtube_scraper

# Scrape PubMed article
python -m scraper.pubmed_scraper
```

### 6. View Results
All output is saved to:
```
output/scraped_data.json
```

### Project Structure
```
TrustSense/
├── scraper/
│   ├── blog_scraper.py
│   ├── youtube_scraper.py
│   └── pubmed_scraper.py
├── scoring/
│   └── trust_score.py
├── utils/
│   ├── tagging.py
│   └── chunking.py
├── output/
│   └── scraped_data.json
├── .env
├── requirements.txt
└── README.md
```

    
