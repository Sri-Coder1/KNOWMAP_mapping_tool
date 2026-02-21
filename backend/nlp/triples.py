def build_triples(relations):
    triples = []

    for subject, relation, obj in relations:
        triples.append({
            "subject": subject,
            "relation": relation,
            "object": obj
        })

    return triples
