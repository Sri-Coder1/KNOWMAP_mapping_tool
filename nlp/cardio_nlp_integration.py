import pandas as pd

# Correct absolute imports
from nlp.nlp_pipeline import run_nlp_pipeline
from graph_builder.graph_builder import build_knowledge_graph
from graph_builder.interactive_graph import create_interactive_graph

# 1️⃣ Load Dataset (correct folder name)
df = pd.read_csv("dataset/cardio_train_.csv", sep=";")

# 2️⃣ Convert Row to Text
def row_to_text(row):
    return (
        f"Patient aged {round(row['age'],2)} years "
        f"has systolic blood pressure {round(row['systolic_bp'],2)} "
        f"and diastolic blood pressure {round(row['diastolic_bp'],2)}. "
        f"Cholesterol level is {row['cholesterol']} "
        f"and glucose level is {row['gluc']}. "
        f"Heart disease status is {row['cardio']}."
    )

# 3️⃣ Extract Triples
all_triples = []

for _, row in df.head(50).iterrows():
    text = row_to_text(row)
    result = run_nlp_pipeline(text)
    all_triples.extend(result["triples"])

print("Total Triples Extracted:", len(all_triples))

# 4️⃣ Domain Mapping
domain_map = {
    "Patient": "Medical",
    "cholesterol": "Medical",
    "glucose": "Medical",
    "heart disease": "Medical",
    "pressure": "Medical",
    "years": "Medical",
    "status": "Medical"
}

# 5️⃣ Build Graph
G = build_knowledge_graph(all_triples, domain_map)

# 6️⃣ Create Interactive Graph
create_interactive_graph(G)