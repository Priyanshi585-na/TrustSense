from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import joblib

# model = KeyBERT(SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2"))
# joblib.dump(model, 'artifacts/keybert.pkl')

model = joblib.load('artifacts/keybert.pkl')

def tagging(text):
    keywords = []
    words = model.extract_keywords(text,use_mmr=True, diversity=0.7)
    for word in words:
        keywords.append(word[0])
    return keywords
