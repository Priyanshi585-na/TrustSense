import joblib

model = joblib.load('artifacts/keybert.pkl')

def tagging(text):
    keywords = []
    words = model.extract_keywords(text,use_mmr=True, diversity=0.7)
    for word in words:
        keywords.append(word[0])
    return keywords
