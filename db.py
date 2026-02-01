import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "scraper_data.db")

def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            category TEXT,
            section TEXT,
            kind TEXT,
            type TEXT,
            number TEXT,
            date TEXT,
            ecli TEXT,
            president TEXT,
            relator TEXT,
            pdf_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(doc, pdf_path, path=DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO documents
        (id, category, section, kind, type, number, date, ecli, president, relator, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doc.get('id'), doc.get('category'), doc.get('section'), doc.get('kind'), doc.get('type'),
        doc.get('number'), doc.get('date'), doc.get('ecli'), doc.get('president'), doc.get('relator'),
        pdf_path
    ))
    conn.commit()
    conn.close()