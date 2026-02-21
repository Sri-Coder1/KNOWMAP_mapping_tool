import pandas as pd

from nlp.nlp_pipeline import run_nlp_pipeline
from graph_builder.graph_builder import build_knowledge_graph
from graph_builder.interactive_graph import create_interactive_graph


# ===============================
# TEXT MODE (Single Sentence)
# ===============================

def run_text_mode():

    text = "AI is transforming healthcare using deep learning models."

    print("\n========== TEXT MODE ==========")
    print("Input Text:")
    print(text)

    result = run_nlp_pipeline(text)

    print("\nCleaned Sentences:")
    print(result["cleaned_sentences"])

    print("\nEntities:")
    print(result["entities"])

    print("\nRelations:")
    print(result["relations"])

    print("\nTriples:")
    print(result["triples"])

    G = build_knowledge_graph(result["triples"])
    create_interactive_graph(G)


# ===============================
# DATASET MODE (Cardio Dataset)
# ===============================

def run_dataset_mode():

    print("\n========== DATASET MODE ==========")

    # ⚠ Make sure folder name matches your project
    df = pd.read_csv("dataset/cardio_train_processed.csv")

    def row_to_text(row):
        return (
            f"Patient has age {round(row['age'],1)} years. "
            f"Patient has systolic pressure {round(row['systolic_bp'],1)} mmHg. "
            f"Patient has diastolic pressure {round(row['diastolic_bp'],1)} mmHg. "
            f"Patient has cholesterol level {row['cholesterol']}. "
            f"Patient has glucose level {row['gluc']}. "
            f"Patient has cardio status {row['cardio']}."
        )

    all_triples = []

    for i, (_, row) in enumerate(df.head(10).iterrows()):

        text = row_to_text(row)
        result = run_nlp_pipeline(text)

        print(f"\n=========== RECORD {i+1} ===========")
        print("Generated Text:")
        print(text)

        print("\nEntities:")
        print(result["entities"])

        print("\nRelations:")
        print(result["relations"])

        print("\nTriples:")
        print(result["triples"])

        all_triples.extend(result["triples"])

    print("\n====================================")
    print("Total Triples Extracted:", len(all_triples))

    domain_map = {
        "Patient": "Medical",
        "age": "Medical",
        "pressure": "Medical",
        "cholesterol": "Medical",
        "glucose": "Medical",
        "status": "Medical"
    }

    G = build_knowledge_graph(all_triples, domain_map)
    create_interactive_graph(G)


# ===============================
# MAIN ENTRY
# ===============================

if __name__ == "__main__":

    print("Choose Mode:")
    print("1 - Text Demo")
    print("2 - Cardio Dataset")

    choice = input("Enter choice: ")

    if choice == "1":
        run_text_mode()
    elif choice == "2":
        run_dataset_mode()
    else:
        print("Invalid choice. Please enter 1 or 2.")