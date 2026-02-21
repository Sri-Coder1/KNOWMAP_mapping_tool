from .preprocessing import nlp

def extract_relations(text: str):
    doc = nlp(text)
    relations = []

    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "VERB":

                subjects = [w.text for w in token.lefts
                            if w.dep_ in ("nsubj", "nsubjpass")]

                objects = [w.text for w in token.rights
                           if w.dep_ in ("dobj", "pobj", "attr")]

                for subj in subjects:
                    for obj in objects:
                        relations.append((subj, token.lemma_, obj))

    return relations
