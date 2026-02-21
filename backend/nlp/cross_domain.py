from .ontology import DOMAIN_KEYWORDS

def classify_entity(entity_text):
    entity_text = entity_text.lower()

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in entity_text:
                return domain

    return "Unknown"


def detect_cross_domain(triples):
    cross_links = []

    for triple in triples:
        subj_domain = classify_entity(triple["subject"])
        obj_domain = classify_entity(triple["object"])

        if (
            subj_domain != obj_domain and
            subj_domain != "Unknown" and
            obj_domain != "Unknown"
        ):
            cross_links.append({
                "subject": triple["subject"],
                "relation": triple["relation"],
                "object": triple["object"],
                "subject_domain": subj_domain,
                "object_domain": obj_domain
            })

    return cross_links
