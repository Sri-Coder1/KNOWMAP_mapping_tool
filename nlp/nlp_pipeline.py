from nlp.preprocessing import preprocess_text
from nlp.ner_spacy import extract_entities
from nlp.relation_extraction import extract_relations

def run_nlp_pipeline(text):

    cleaned = preprocess_text(text)
    entities = extract_entities(text)
    relations = extract_relations(text)

    triples = [
        (rel["subject"], rel["relation"], rel["object"])
        for rel in relations
    ]

    return {
        "cleaned_sentences": cleaned,
        "entities": entities,
        "relations": relations,
        "triples": triples
    }