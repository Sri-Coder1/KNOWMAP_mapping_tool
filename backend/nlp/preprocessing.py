import spacy

# Load model once (global)
nlp = spacy.load("en_core_web_sm")

def preprocess_text(text: str):
    if not text:
        return None
    return nlp(text)
