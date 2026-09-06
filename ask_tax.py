"""
ask_tax.py - Tax RAG with conversational memory, source citations, and backend toggle.
"""
import os, json, numpy as np, faiss, requests
from sentence_transformers import SentenceTransformer
import sys

OLLAMA_URL = "http://localhost:11434"
VAULT_IDX = r"C:\Users\LENOVO\tag-rag\index"

# Backend toggle: ollama (default, free) or bedrock (when AWS quota resets)
BACKEND = "ollama"  # Change to "bedrock" when quota is available

# Ollama model (local, free)
OLLAMA_MODEL = "qwen3:8b"

# Bedrock model (cloud, requires AWS quota)
# Use the inference profile ARN for Claude 3 Haiku (works with cross-region routing)
BEDROCK_MODEL_ID = "arn:aws:bedrock:us-east-1:275956851567:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_REGION = "us-east-1"


def load_index():
    print(f"[1/4] Loading FAISS index from {VAULT_IDX}...")
    index = faiss.read_index(os.path.join(VAULT_IDX, "tax.index"))
    with open(os.path.join(VAULT_IDX, "docs.json"), encoding="utf-8") as f:
        docs = json.load(f)
    print(f"      Loaded {len(docs)} chunks from index")
    return index, docs


def load_embedder():
    print(f"[2/4] Loading embedding model (nomic-embed-text-v1.5)...")
    return SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)


def ollama_generate(prompt: str) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 500}
        },
        timeout=120
    )
    if resp.status_code != 200:
        return f"ERROR: Ollama returned {resp.status_code}: {resp.text[:500]}"
    return resp.json()["response"]


def bedrock_generate(prompt: str) -> str:
    import boto3
    bedrock = boto3.client(service_name='bedrock-runtime', region_name=BEDROCK_REGION)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    }
    resp = bedrock.invoke_model(
        body=json.dumps(body).encode('utf-8'),
        modelId=BEDROCK_MODEL_ID,
        accept='application/json',
        contentType='application/json'
    )
    result = json.loads(resp['body'].read())
    return result['content'][0]['text']


def generate(prompt: str) -> str:
    if BACKEND == "ollama":
        return ollama_generate(prompt)
    elif BACKEND == "bedrock":
        return bedrock_generate(prompt)
    else:
        return f"ERROR: Unknown backend '{BACKEND}'"


def ask_tax(question: str, top_k: int = 2, history: list = None) -> tuple[str, list]:
    """
    Returns (answer, retrieved_sources)
    retrieved_sources is a list of {source, snippet} for citations.
    """
    history = history or []
    print(f"\n[Query] {question}")
    q_emb = embed.encode([question])
    D, I = index.search(np.array(q_emb).astype('float32'), top_k)
    print(f"[Retrieve] Found {len(I[0])} relevant chunks")

    retrieved = []
    for idx in I[0]:
        retrieved.append({
            "source": docs[idx].get("source", "unknown"),
            "snippet": docs[idx]["text"][:300]
        })

    context = "\n\n---\n\n".join([docs[i]["text"][:2000] for i in I[0]])

    history_text = ""
    if history:
        history_text = "\n\nPREVIOUS CONVERSATION:\n" + "\n".join(
            f"{turn['role'].upper()}: {turn['content']}" for turn in history[-4:]
        )

    prompt = f"""You are a tax expert. Answer the question using ONLY the excerpts from IRS Publication 17 provided below.
If the answer is not in the excerpts, say "I don't know based on the provided document."

EXCERPTS:
{context}
{history_text}

QUESTION: {question}

ANSWER:"""

    print(f"[Generate] Sending to {BACKEND}...")
    answer = generate(prompt)
    return answer, retrieved


def format_citations(retrieved: list) -> str:
    """Format source citations for the answer."""
    if not retrieved:
        return ""
    sources = sorted(set(r["source"] for r in retrieved))
    return "\n\n[Sources: " + ", ".join(sources) + "]"


# === INIT ===
print("=" * 60)
print(f"Tax RAG Pipeline (backend: {BACKEND})")
print("=" * 60)
index, docs = load_index()
embed = load_embedder()
print(f"[3/4] Backend: {BACKEND}")
print(f"[4/4] Ready!\n")


def chat_mode():
    """Interactive multi-turn chat with memory."""
    history = []
    print("Chat mode. Type 'quit' to exit.\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
        if not q or q.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            return
        answer, sources = ask_tax(q, history=history)
        citations = format_citations(sources)
        full_response = answer + citations
        print(f"\nAssistant: {full_response}\n")
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": full_response})


def one_shot_mode(question: str):
    answer, sources = ask_tax(question)
    citations = format_citations(sources)
    print(f"\n{'='*60}\n{answer}{citations}\n{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python ask_tax.py "your question"          # one-shot Q&A')
        print('  python ask_tax.py --chat                    # multi-turn chat')
        sys.exit(1)
    if sys.argv[1] == "--chat":
        chat_mode()
    else:
        one_shot_mode(" ".join(sys.argv[1:]))
