import spacy

nlp = spacy.load("en_core_web_sm")

def extract_relations(text):
    doc = nlp(text)
    relations = []

    for token in doc:
        if token.lemma_ in ["have", "be", "show", "indicate"]:  
            if token.dep_ == "ROOT":

                subjects = [
                    w for w in token.lefts
                    if w.dep_ in ("nsubj", "nsubjpass")
                ]

                objects = [
                    w for w in token.rights
                    if w.dep_ in ("dobj", "pobj", "attr")
                ]

                if subjects and objects:
                    relations.append({
                        "subject": subjects[0].text,
                        "relation": token.lemma_,
                        "object": objects[0].text
                    })

    return relations