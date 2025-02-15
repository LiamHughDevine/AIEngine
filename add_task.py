import faiss
import sqlite3
from sentence_transformers import SentenceTransformer


def add_task(task: str, action: str, db_name: str = "context") -> None:
    con = sqlite3.connect(f"{db_name}.db")
    cur = con.cursor()
    data = [task, action]
    print("TEST")
    cur.execute("INSERT INTO metadata (task, action) VALUES (?, ?)", data)
    con.commit()

    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(f"{db_name}_faiss_index.bin")

    encoding = model.encode([task])
    index.add(encoding)

    faiss.write_index(index, f"{db_name}_faiss_index.bin")


if __name__ == "__main__":
    add_task("Blue dog", "Fido says woof")
