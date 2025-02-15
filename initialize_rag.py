import faiss
import sqlite3
from sentence_transformers import SentenceTransformer


def initialize_rag(db_name: str = "context") -> None:
    con = sqlite3.connect(f"{db_name}.db")
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE metadata (
        id INTEGER PRIMARY KEY,
        task TEXT,
        action TEXT
    )"""
    )
    con.commit()

    model = SentenceTransformer("all-MiniLM-L6-v2")
    # We initialise the index with an empty vector, it will also ensure that
    # the sql database and vector database id's are consistent
    vectors = model.encode(["UNKNOWN"])
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, f"{db_name}_faiss_index.bin")


if __name__ == "__main__":
    initialize_rag()
