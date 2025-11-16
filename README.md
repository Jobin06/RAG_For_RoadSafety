An AI-powered assistant that analyzes road signage problems and provides accurate, IRC:67-2022 compliant solutions using Retrieval-Augmented Generation (RAG), sentence-transformer embeddings, and Groq LLaMA 3.1.
Overview:
Road authorities and engineers often struggle with:
•	Missing or damaged traffic signs
•	Incorrect sign dimensions
•	Wrong placement or height
•	Low-visibility signage
•	Time-consuming manual referencing of IRC standards

This project solves that problem through an intelligent assistant that:
1.	Accepts a user query describing a road issue.
2.	Retrieves relevant rules from IRC:67-2022 using embeddings.
3.	Generates precise, expert guidance using Groq LLaMA 3.1.
4.	Displays the response in a modern chat-based interface.
The result is a fast, accurate, and scalable tool that significantly reduces the time needed to diagnose road signage issues.

Tech Stack
Backend:
•	FastAPI – Lightweight, fast REST API
•	Sentence Transformers (all-MiniLM-L6-v2) – For generating embeddings
•	NumPy – Vector similarity for retrieval
•	Groq LLaMA 3.1 (8B Instant) – High-speed LLM inference
•	RAG Pipeline – Custom-built retrieval + generation system
•	Python-dotenv – API key management

Frontend:
•	HTML, CSS, JavaScript – No frameworks
•	Message bubbles, typing indicator, collapsible evidence section

How It Works (Architecture):
User Query → Frontend → FastAPI Backend
          → Embedding Retrieval (Sentence Transformers)
          → Contextual Prompt (RAG)
          → Groq LLaMA 3.1 Response
          → JSON Output → Frontend Chat UI
The system also includes a custom Question Type Classifier:
•	Fact Questions → Short, direct answers
•	Scenario Questions → Step-by-step repair or compliance recommendations

Project Structure:
main_folder
│
├── backend/
│   ├── api.py
│   ├── rag_road_helper.py
│   ├── requirements.txt
│   ├── .env
│   └── data/road_issues_example.json
│
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
  	
Installation & Usage
Backend Setup:
cd backend
pip install -r requirements.txt
Set your Groq API key:
setx GROQ_API_KEY "your_api_key_here"
Run the API server:
python api.py

Frontend:
Simply open:
frontend/index.html
in any browser.

Features:
•	RAG-powered retrieval for high accuracy
•	Groq-powered fast LLM inference
•	Supports IRC:67-2022 road signage rules
•	Shows referenced documents for transparency
•	Auto question classification (fact vs scenario)
•	Completely free to run locally

Why This Project Stands Out:
•	Designed for road engineers, authorities, and city planners
•	Converts complex IRC standards into instant actionable insights
•	Increases road safety by reducing misinterpretation of rules
•	Built using modern AI architecture (RAG + Groq LLM)

