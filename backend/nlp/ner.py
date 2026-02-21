from .preprocessing import nlp

def extract_entities(text: str):
    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities
