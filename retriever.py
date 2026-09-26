import json
import numpy as np
from build_embeddings import get_embedding  # reuse karenge
import yaml


with open("table_embeddings.json") as f:
    table_embeddings = json.load(f)

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def get_relevant_tables(question: str, top_k: int = 3):
    question_embedding = get_embedding(question)
    
    scores = {}
    for table_name, table_embedding in table_embeddings.items():
        scores[table_name] = cosine_similarity(question_embedding, table_embedding)
    
    sorted_tables = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [table for table, score in sorted_tables[:top_k]]


def build_schema_text(table_names):
    with open("catalog.yaml") as f:
        catalog = yaml.safe_load(f)
    
    schema_parts = []
    for table_name in table_names:
        table_info = catalog["tables"][table_name]
        columns = ", ".join(table_info["columns"].keys())
        schema_parts.append(f"- {table_name}({columns}): {table_info['description']}")
    
    return "\n".join(schema_parts)


if __name__ == "__main__":
    result = get_relevant_tables("How many refunds happened last month?")
    print(result)