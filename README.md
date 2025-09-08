# 🧠 OkooAI — Tourism Assistant Powered by RAG

OkooAI is a Retrieval-Augmented Generation (RAG) system built with LangChain, FastAPI, and ChromaDB. It answers tourism-related questions about Ethiopia using real documents, strict fallback logic, and adaptive routing.

## 🚀 Features

- ✅ Naive + Adaptive RAG pipeline
- ✅ LangGraph-based intent routing
- ✅ Strict fallback: no hallucinations
- ✅ Modular nodes for planning, comparison, exploration
- ✅ PDF ingestion and chunking
- ✅ Ollama-powered local LLM (Qwen 0.5b)
- ✅ FastAPI backend with clean endpoints

## 🧱 Architecture

```bash

User Query
   │
   ▼
Intent Classifier ──► LangGraph Router
   │                      │
   ▼                      ▼
Retriever           ┌─────────────┐
   │                │ Nodes:      │
   ▼                │ - ask_fact  │
LLM + Prompt        │ - plan_trip │
   │                │ - compare   │
   ▼                │ - explore   │
Reflection Node ◄───┘
   │
   ▼
Final Answer + Source Chunks

```bash

## 📂 Project Structure

```bash
advanced_rag_ai/
├── api/
│   ├── main.py               # FastAPI entry point
│   ├── tourism_graph.py      # LangGraph workflow
│   ├── planner_node.py       # Trip planner logic
│   ├── hotel_comparison_node.py
│   ├── explore_place_node.py
│   ├── intent_classifier.py
│   ├── adaptive_retriever.py
│   └── self_reflective_rag.py
├── data/                     # Indexed tourism PDFs
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🧪 Demo Instructions

### 1. Start Ollama

```bash
ollama run qwen:0.5b
```

### 2. Run the API

```bash
uvicorn api.main:app --reload
```

### 3. Test the Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "question": "Plan a trip to Gondar", "model": "qwen:0.5b"}'
```

### 4. Upload a PDF

``` bash

curl -X POST http://localhost:8000/upload \
  -F "file=@data/03_Gondar_Bahir_Dar_Lake_Tana_Blue_Nile.pdf"
```

## 📦 Deployment

Use Docker for production:

```bash
docker build -t okooai .
docker run -p 8000:8000 okooai
```

## 📚 Tech Stack

- Python 3.11+
- LangChain + LangGraph
- ChromaDB
- Ollama (Qwen 0.5b)
- FastAPI
- Docker

## 👨‍💻 Built by Segni Abera

Backend-focused developer, product architect, and technical lead. Specializes in scalable APIs, modular backend systems, and founder-grade polish.

---

## 🎬 Demo Script

Here’s how to present OkooAI in a live demo or video:

> “Welcome to OkooAI — a tourism assistant for Ethiopia powered by Retrieval-Augmented Generation. Let’s ask it:  
> _‘Plan a trip to Gondar.’_  
> The system routes this to the trip planner node, retrieves chunks from our indexed tourism PDFs, and generates a grounded itinerary.  
> Now let’s try: _‘Who won the African Cup in 2022?’_  
> Since that’s not in our documents, the system responds:  
> _‘I do not know and it is not in the data and context provided to me.’_  
> No guessing. No hallucinations.  
> That’s founder-grade grounding.”

---

Let me know when you’ve added this to your repo — and we’ll jump into **Day 3: Reflection and Hallucination Detection**. Founder-grade polish, no gaps.
