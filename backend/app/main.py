import json
from pathlib import Path
import networkx as nx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Tell Python exactly where backend/.env is located
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="Spotify RAG + KG Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = BASE_DIR / "data" / "spotify_data.json"
INDEX_PATH = BASE_DIR / "faiss_index"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# 1. Load Data Layer (DL) & Build Knowledge Graph (KG)
with open(DATA_PATH, "r", encoding="utf-8") as f:
    spotify_records = json.load(f)

kg = nx.Graph()
docs = []

for item in spotify_records:
    kg.add_edge(item["track"], item["artist"], relation="PERFORMED_BY")
    kg.add_edge(item["track"], item["genre"], relation="HAS_GENRE")
    kg.add_edge(item["track"], item["mood"], relation="HAS_MOOD")
    kg.add_edge(item["track"], item["playlist"], relation="FEATURED_IN")

    text = (
        f"Track: {item['track']} | Artist: {item['artist']} | "
        f"Album: {item['album']} | Genre: {item['genre']} | "
        f"Mood: {item['mood']} | Playlist: {item['playlist']} | "
        f"Details: {item['details']}"
    )
    docs.append(Document(page_content=text, metadata={"track": item["track"], "artist": item["artist"]}))

# 2. Build or Load Local FAISS Vector DB
if INDEX_PATH.exists():
    vector_db = FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
else:
    vector_db = FAISS.from_documents(docs, embeddings)
    vector_db.save_local(str(INDEX_PATH))


def get_kg_context(track_name: str) -> str:
    if track_name not in kg:
        return ""
    connections = []
    for neighbor in kg.neighbors(track_name):
        rel = kg[track_name][neighbor]["relation"]
        connections.append(f"{track_name} --[{rel}]--> {neighbor}")
        for second_hop in kg.neighbors(neighbor):
            if second_hop != track_name:
                connections.append(f"Related via {neighbor}: {second_hop}")
    return "\n".join(set(connections))


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def health_check():
    return {"status": "Spotify RAG + KG API is running"}


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    retrieved_docs = vector_db.similarity_search(req.question, k=2)

    vdb_context = "\n".join([d.page_content for d in retrieved_docs])
    kg_contexts = [get_kg_context(d.metadata["track"]) for d in retrieved_docs]
    kg_context = "\n".join(kg_contexts)

    prompt = f"""You are a helpful Spotify Music Assistant. Answer the user's question using ONLY the retrieved Vector DB context and Knowledge Graph connections below.

[Vector DB Results]
{vdb_context}

[Knowledge Graph Connections]
{kg_context}

User Question: {req.question}
"""
    response = llm.invoke(prompt)
    return {
        "answer": response.content,
        "retrieved_tracks": [d.metadata["track"] for d in retrieved_docs],
        "kg_relations": kg_context.splitlines()
    }