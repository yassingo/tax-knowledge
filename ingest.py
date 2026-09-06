import os, json, fitz, numpy as np, faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path

VAULT = Path(r"C:\Users\LENOVO\Obsidian\TaxVault")
OUT   = Path(r"C:\Users\LENOVO\tag-rag\index")
OUT.mkdir(exist_ok=True)

# Correct HuggingFace model ID
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

docs = []
embs = []

for pdf in VAULT.rglob("*.pdf"):
    text = ""
    with fitz.open(pdf) as doc:
        for page in doc:
            text += page.get_text()
    # Simple chunking (~500 tokens ~ 2000 chars)
    for i in range(0, len(text), 500):
        chunk = text[i:i+500]
        if chunk.strip():
            docs.append({"source": pdf.name, "text": chunk})
            embs.append(model.encode(chunk))

# Build FAISS index
dim = len(embs[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embs).astype('float32'))
faiss.write_index(index, str(OUT/"tax.index"))
with open(OUT/"docs.json","w",encoding="utf-8") as f:
    json.dump(docs, f, ensure_ascii=False, indent=2)
print(f"Indexed {len(docs)} chunks from {VAULT}")
