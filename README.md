Spotify RAG + Knowledge Graph Assistant

A full-stack AI music recommendation and discovery web application combining Retrieval-Augmented Generation (RAG) via FAISS vector search with Knowledge Graph (KG) traversal via NetworkX, powered by FastAPI and OpenAI.

Live Demo: https://braj23.sbs

Architecture Overview

User Browser (HTTPS)
       │
       ▼
Nginx Reverse Proxy (SSL via Let's Encrypt / Certbot)
   ├── /       ──► Frontend Container (HTML/CSS/JS on Port 3000)
   └── /api/   ──► Backend Container  (FastAPI + FAISS + NetworkX on Port 8000)
                          │
                          ▼
                     OpenAI API (Embeddings & Chat Completion)


Tech Stack

Backend: Python 3.11, FastAPI, Uvicorn, LangChain

Vector Store (RAG): FAISS (semantic similarity search over track metadata)

Knowledge Graph: NetworkX (multi-hop relationship traversal across artists, genres, moods, and playlists)

LLM & Embeddings: OpenAI API

Frontend: Vanilla HTML5, CSS3, JavaScript (Fetch API)

Infrastructure & Deployment: Docker, Docker Compose, Nginx, Certbot (Let's Encrypt), Ubuntu VPS

Project Structure

spotify-web-app/
├── backend/
│   ├── app/
│   │   └── main.py           # FastAPI application, FAISS search & KG logic
│   ├── Dockerfile            # Backend container build instructions
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables (not tracked in Git)
├── frontend/
│   ├── index.html            # Chatbot UI & API integration
│   └── Dockerfile            # Frontend static server container
├── docker-compose.yml        # Multi-container orchestration
├── .gitignore
└── README.md


Local Development Setup

Prerequisites

Docker & Docker Compose installed

An active OpenAI API key

Steps

Clone the repository:

git clone https://github.com/raj230987-star/spotify-web-app.git
cd spotify-web-app


Configure environment variables:
Create backend/.env and add your OpenAI API key:

OPENAI_API_KEY=sk-your-actual-openai-api-key


Build and run with Docker Compose:

docker compose up -d --build


Access the application:

Frontend UI: http://localhost:3000

Backend API Docs (Swagger): http://localhost:8000/docs

Production Deployment (Ubuntu VPS + Nginx + SSL)

Clone and start containers on VPS:

git clone https://github.com/raj230987-star/spotify-web-app.git
cd spotify-web-app
echo "OPENAI_API_KEY=sk-your-actual-openai-api-key" > backend/.env
docker compose up -d --build


Configure Nginx Reverse Proxy (/etc/nginx/sites-available/spotify-app):

Proxy / to http://127.0.0.1:3000

Proxy /api/ to http://127.0.0.1:8000/

Configure DNS & SSL:

Point domain A record (@) to the VPS IP address.

Issue and auto-renew SSL certificates using Certbot:

certbot --nginx -d braj23.sbs


Updating the Live Application

To deploy new changes pushed to GitHub:

cd ~/spotify-web-app
git pull origin main
docker compose up -d --build
