import sqlite3
from typing import List, Dict

DB_PATH = "./scraper_data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def fetch_all_documents() -> List[Dict]:
    """
    Read all documents from the database.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM documents")
    rows = cur.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def fetch_documents_by_category(category: str) -> List[Dict]:
    """
    Read documents filtered by category (e.g. CIVILE, PENALE).
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM documents WHERE category = ?",
        (category.upper(),)
    )
    rows = cur.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def fetch_document_by_id(doc_id: str) -> Dict | None:
    """
    Read a single document by ID.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM documents WHERE id = ?",
        (doc_id,)
    )
    row = cur.fetchone()

    conn.close()
    return dict(row) if row else None


def main():
    print(">>> DB READER STARTED\n")

    # Example 1: fetch all documents
    docs = fetch_all_documents()
    print(f"[INFO] Total documents in DB: {len(docs)}\n")

    for i, doc in enumerate(docs[:5], start=1):
        print(f"{i}. {doc['id']} | {doc['number']} | {doc['date']} | {doc['type']}")

    # Example 2: fetch by category
    print("\n--- CIVILE DOCUMENTS ---")
    civile_docs = fetch_documents_by_category("CIVILE")
    print(f"Found {len(civile_docs)} CIVILE documents")

    # Example 3: fetch single document
    if docs:
        sample_id = docs[0]["id"]
        print(f"\n--- SINGLE DOCUMENT ({sample_id}) ---")
        single_doc = fetch_document_by_id(sample_id)
        print(single_doc)


if __name__ == "__main__":
    main()
