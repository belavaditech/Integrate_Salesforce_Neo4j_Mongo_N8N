import os
import json
import re
from typing import List, Dict, Any

from openai import OpenAI
from pymongo import MongoClient
from neo4j import GraphDatabase
from pypdf import PdfReader
from dotenv import load_dotenv

# ==========================================================
# Load .env configuration
# ==========================================================

load_dotenv()

OPENAI_MODEL_TEXT = os.getenv("OPENAI_MODEL_TEXT", "gpt-4o-mini")
OPENAI_MODEL_EMBED = os.getenv("OPENAI_MODEL_EMBED", "text-embedding-3-small")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "biomolecules")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "chunks")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

ENV_INTERACTIVE = os.getenv("INTERACTIVE", "true").lower() == "true"
CLI_INTERACTIVE_OVERRIDE = None

# ==========================================================
# Connect Clients
# ==========================================================

print("🔌 Loading config…")
print("Neo4j URI =", repr(NEO4J_URI))

openai_client = OpenAI()
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
mongo_col = mongo_db[MONGO_COLLECTION_NAME]

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

# ==========================================================
# Interactive Helpers
# ==========================================================

def is_interactive() -> bool:
    if CLI_INTERACTIVE_OVERRIDE is not None:
        return CLI_INTERACTIVE_OVERRIDE
    return ENV_INTERACTIVE

def ask(prompt: str, default="y") -> bool:
    if not is_interactive():
        return True
    ans = input(f"{prompt} (y/n, default={default}): ").strip().lower()
    return ans == "" and default == "y" or ans.startswith("y")

def pause(msg="Press Enter to continue..."):
    if is_interactive():
        input(msg)

# ==========================================================
# Sanitization Helpers
# ==========================================================

def sanitize_label(raw_type: str) -> str:
    if not raw_type:
        return "Entity"
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", raw_type)
    tokens = cleaned.strip().split()
    return "".join(t.capitalize() for t in tokens) if tokens else "Entity"

def sanitize_relation(raw: str) -> str:
    return sanitize_label(raw).upper() if raw else "RELATED_TO"

# ==========================================================
# Relation Normalizer
# ==========================================================

def normalize_relation(r):
    if not isinstance(r, dict):
        return None

    subject = (
        r.get("subject") or
        r.get("source") or
        r.get("head") or
        r.get("entity1") or
        r.get("from") or
        r.get("subj")
    )

    object_ = (
        r.get("object") or
        r.get("target") or
        r.get("tail") or
        r.get("entity2") or
        r.get("to") or
        r.get("obj")
    )

    predicate = (
        r.get("predicate") or
        r.get("relation") or
        r.get("rel") or
        r.get("type") or
        r.get("action")
    )

    subj_type = (
        r.get("subject_type") or
        r.get("source_type") or
        "Entity"
    )

    obj_type = (
        r.get("object_type") or
        r.get("target_type") or
        "Entity"
    )

    if not subject or not object_ or not predicate:
        return None

    return {
        "subject": subject,
        "object": object_,
        "predicate": predicate,
        "subject_type": subj_type,
        "object_type": obj_type
    }

# ==========================================================
# PDF Processing
# ==========================================================

def load_pdf_pages(pdf_path):
    print("📄 Loading PDF:", pdf_path)
    reader = PdfReader(pdf_path)
    pages = []
    for i, p in enumerate(reader.pages):
        pages.append({"page": i+1, "text": p.extract_text() or ""})
    return pages

def chunk_pdf(pages, chunk_size, overlap):
    print("✂️ Chunking PDF...")
    chunks = []
    buf = ""
    start = pages[0]["page"]
    end = start
    idx = 0

    for p in pages:
        for line in p["text"].split("\n"):
            line = line.strip()
            if not line:
                continue

            if len(buf) + len(line) > chunk_size:
                chunks.append({
                    "chunk_id": f"chunk_{idx}",
                    "text": buf.strip(),
                    "start_page": start,
                    "end_page": end,
                })
                idx += 1
                buf = buf[-overlap:] + " " + line
                start = end
            else:
                buf += " " + line
                end = p["page"]

    if buf.strip():
        chunks.append({
            "chunk_id": f"chunk_{idx}",
            "text": buf.strip(),
            "start_page": start,
            "end_page": end,
        })

    print("→ Created", len(chunks), "chunks.")
    return chunks

# ==========================================================
# OpenAI Extraction
# ==========================================================

def extract_entities_relations(text):
    system_prompt = (
        "Extract biomedical/scientific entities and relations in strict JSON:\n"
        "{ 'entities': [...], 'relations': [...] }"
    )
    resp = openai_client.chat.completions.create(
        model=OPENAI_MODEL_TEXT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    msg = resp.choices[0].message.content
    try:
        return json.loads(msg)
    except:
        first = msg.find("{")
        last = msg.rfind("}")
        return json.loads(msg[first:last+1])

def get_embedding(text):
    res = openai_client.embeddings.create(
        model=OPENAI_MODEL_EMBED,
        input=text
    )
    return res.data[0].embedding

# ==========================================================
# MongoDB Index (Safe, Silent)
# ==========================================================

VECTOR_INDEX_SUPPORTED = True
VECTOR_INDEX_CHECKED = False

def create_vector_index(dims=1536):
    global VECTOR_INDEX_SUPPORTED, VECTOR_INDEX_CHECKED

    if VECTOR_INDEX_CHECKED and not VECTOR_INDEX_SUPPORTED:
        return

    print("📦 Checking MongoDB vector index...")

    try:
        mongo_db.command({
            "createIndexes": MONGO_COLLECTION_NAME,
            "indexes": [
                {
                    "name": "embedding_vector_index",
                    "key": {"embedding": "vector"},
                    "vector": {
                        "type": "float32",
                        "dimensions": dims,
                        "similarity": "cosine"
                    }
                }
            ]
        })
        print("✅ Vector index created or already exists.")

    except Exception as e:
        msg = str(e)

        if "disallowed in this Atlas tier" in msg:
            print("ℹ️ Atlas free tier does NOT support vector indexes. Skipping permanently.")
            VECTOR_INDEX_SUPPORTED = False
            VECTOR_INDEX_CHECKED = True
            return

        if "already exists" in msg:
            print("ℹ️ Vector index already exists.")
            VECTOR_INDEX_CHECKED = True
            return

        print("⚠️ Unexpected index error:", e)

    VECTOR_INDEX_CHECKED = True

# ==========================================================
# Mongo Write
# ==========================================================

def save_to_mongo(paper_id, chunk, entities, relations, embedding):
    mongo_col.insert_one({
        "paper_id": paper_id,
        "chunk_id": chunk["chunk_id"],
        "text": chunk["text"],
        "embedding": embedding,
        "metadata": {
            "start_page": chunk["start_page"],
            "end_page": chunk["end_page"],
            "entities": entities,
            "relations": relations
        }
    })

# ==========================================================
# Neo4j Write (Entity + Relation Sanitized)
# ==========================================================

def push_to_neo4j(entities, relations):
    print("   🕸 Pushing to Neo4j...")

    with neo4j_driver.session() as session:

        # --------- NODES ----------
        for e in entities:
            if isinstance(e, str):
                e = {"name": e, "type": "Entity"}

            if not isinstance(e, dict):
                print("⚠️ Skipping invalid entity:", e)
                continue

            name = e.get("name")
            etype = sanitize_label(e.get("type", "Entity"))

            if not name:
                print("⚠️ Skipping no-name entity:", e)
                continue

            try:
                session.run(
                    f"MERGE (n:{etype} {{name:$name}})",
                    name=name
                )
            except Exception as neo_err:
                print(f"❌ Node insert failed for {name}: {neo_err}")

        # --------- RELATIONSHIPS ----------
        for r in relations:
            nr = normalize_relation(r)

            if not nr:
                print("⚠️ Skipping relation with missing ends:", r)
                continue

            subj = nr["subject"]
            obj = nr["object"]
            pred = sanitize_relation(nr["predicate"])
            stype = sanitize_label(nr["subject_type"])
            otype = sanitize_label(nr["object_type"])

            try:
                session.run(
                    f"""
                    MATCH (a:{stype} {{name:$subj}})
                    MATCH (b:{otype} {{name:$obj}})
                    MERGE (a)-[:{pred}]->(b)
                    """,
                    subj=subj,
                    obj=obj
                )
            except Exception as neo_err:
                print(f"❌ Relationship failed: {subj} -[{pred}]-> {obj}\n{neo_err}")

# ==========================================================
# Main Pipeline
# ==========================================================

def process_pdf(pdf_path, paper_id):

    pages = load_pdf_pages(pdf_path)

    if is_interactive() and ask("Preview first pages?"):
        for p in pages[:2]:
            print(f"[Page {p['page']}] {p['text'][:300]}\n")
        pause()

    chunks = chunk_pdf(pages, CHUNK_SIZE, CHUNK_OVERLAP)

    if is_interactive() and ask("Preview first chunks?"):
        for c in chunks[:2]:
            print(c["chunk_id"], c["text"][:300])
        pause()

    create_vector_index()

    for i, chunk in enumerate(chunks):
        print(f"\n=== Processing chunk {i+1}/{len(chunks)} ===")

        if is_interactive() and not ask("Process this chunk?"):
            continue

        extraction = extract_entities_relations(chunk["text"])
        entities = extraction.get("entities", [])
        relations = extraction.get("relations", [])

        if is_interactive() and ask("Show extracted JSON?"):
            print(json.dumps(extraction, indent=2))
            pause()

        embedding = get_embedding(chunk["text"])

        if not is_interactive() or ask("Save to Mongo?"):
            save_to_mongo(paper_id, chunk, entities, relations, embedding)

        if relations and (not is_interactive() or ask("Push to Neo4j?")):
            push_to_neo4j(entities, relations)

    print("\n🎉 DONE — MongoDB + Neo4j updated successfully.")

# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("--paper-id", default="paper-001")
    parser.add_argument("--non-interactive", action="store_true")

    args = parser.parse_args()

    CLI_INTERACTIVE_OVERRIDE = not args.non_interactive

    process_pdf(args.pdf_path, args.paper_id)

