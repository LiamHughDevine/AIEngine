import faiss
import numpy as np
import sqlite3
from sentence_transformers import SentenceTransformer


def retrieve(query: str, k: int, db_name: str = "context") -> list[str]:
    # Model for encoding query - must be same as model for faiss vector database
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(f"{db_name}_faiss_index.bin")
    # SQLite database for accessing plain text version
    con = sqlite3.connect(f"{db_name}.db")
    cur = con.cursor()

    new_vec = model.encode(query)
    svec = np.array(new_vec).reshape(1, -1)
    faiss.normalize_L2(svec)
    _, indices = index.search(svec, k=k)

    context = []
    row_indices = indices.tolist()[0]

    for row in row_indices:
        result = cur.execute(
            f"""SELECT task, action
            FROM metadata
            WHERE id={row}"""
        )
        for value in result:
            context.append(value)

    return context


if __name__ == "__main__":
    print(retrieve("Small dog", 2))
