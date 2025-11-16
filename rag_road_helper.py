import json
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env (GROQ_API_KEY)
load_dotenv()


# -----------------------------
# Data structure
# -----------------------------

@dataclass
class RoadIssue:
    problem: str
    category: str
    type: str
    description: str
    code: str
    clause: str


# -----------------------------
# Database loading
# -----------------------------

def load_road_issues(json_path: str) -> List[RoadIssue]:
    if not os.path.exists(json_path):
        print(f"[ERROR] Database file not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    issues: List[RoadIssue] = []
    for item in raw:
        issues.append(
            RoadIssue(
                problem=item.get("problem", ""),
                category=item.get("category", ""),
                type=item.get("type", ""),
                description=item.get("description", "") or item.get("data", ""),
                code=item.get("code", ""),
                clause=str(item.get("clause", "")),
            )
        )

    print(f"[INFO] Loaded {len(issues)} issues from database.")
    return issues


def issue_to_embedding_text(issue: RoadIssue) -> str:
    return (
        f"Problem: {issue.problem}\n"
        f"Category: {issue.category}\n"
        f"Type: {issue.type}\n"
        f"Code: {issue.code}\n"
        f"Clause: {issue.clause}\n"
        f"Description: {issue.description}"
    )


# -----------------------------
# Embedding + Retrieval
# -----------------------------

class RoadIssueRetriever:
    def __init__(self, issues: List[RoadIssue], embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.issues = issues
        print(f"[INFO] Loading embedding model: {embedding_model}")
        self.model = SentenceTransformer(embedding_model)

        print("[INFO] Encoding issues...")
        texts = [issue_to_embedding_text(i) for i in issues]
        self.embeddings = self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )

    def retrieve(self, query: str, top_k: int = 2) -> List[Tuple[RoadIssue, float]]:
        query_emb = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )[0]
        scores = np.dot(self.embeddings, query_emb)
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(self.issues[i], float(scores[i])) for i in top_idx]


# -----------------------------
# Groq LLM wrapper
# -----------------------------

class RoadIssueLLM:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("[ERROR] GROQ_API_KEY not found. Please set it in .env")
            sys.exit(1)

        self.client = Groq(api_key=api_key)
        # ✅ Correct, current Groq model
        self.model = "llama-3.1-8b-instant"

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior traffic engineer specializing in IRC:67-2022 road signage rules."
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.6,
            top_p=0.9,
        )
        # groq-py uses .message.content
        return response.choices[0].message.content.strip()


# -----------------------------
# RAG Pipeline
# -----------------------------

class RoadRAGPipeline:
    def __init__(self, db_path: str):
        self.issues = load_road_issues(db_path)
        self.retriever = RoadIssueRetriever(self.issues)
        self.llm = RoadIssueLLM()

    def build_context(self, retrieved: List[Tuple[RoadIssue, float]]) -> str:
        blocks = []
        for i, (issue, score) in enumerate(retrieved, start=1):
            blocks.append(
                f"[Doc {i} | Score={score:.3f}]\n"
                f"Problem: {issue.problem}\n"
                f"Category: {issue.category}\n"
                f"Type: {issue.type}\n"
                f"Code: {issue.code}\n"
                f"Clause: {issue.clause}\n"
                f"Description: {issue.description}\n"
            )
        return "\n".join(blocks)

    def build_prompt(self, query: str, context: str) -> str:
        return f"""
You are an IRC:67-2022 road signage expert.

USER QUESTION:
{query}

REFERENCE DOCUMENTS:
{context}

Your job is to answer using ONLY the information in the reference documents.

=====================================================
📌 QUESTION TYPE CLASSIFICATION (STRICT RULES)
=====================================================

Classify the user question into one of TWO types:

-----------------------------------------------------
TYPE 1 — FACT QUESTION (short, direct, informational)

Use this ONLY if the question:
- asks for a specific fact (size, clause, placement rule, etc.)
- contains NO scenario, NO location, NO issue description
- does NOT describe anything that is broken, missing, damaged, tilted, obstructed, etc.
- is less than ~20 words and not action-based

Examples:
"What is the STOP sign size for speeds above 65 km/h?"
"What clause applies to Minimum Speed signs?"

👉 RESPONSE RULE:
Give a short factual answer (1–3 sentences). No steps, no repairs.

-----------------------------------------------------
TYPE 2 — SCENARIO QUESTION (real situation, issue, problem)

Use this if the question:
- describes a missing, damaged, faded, broken, or misinstalled sign
- mentions an intersection, road segment, or real-world location
- asks "What should be done?" or implies an action
- requires recommendations or compliance checks

Examples:
"A STOP sign is missing near a T-intersection. What should be installed?"
"The speed limit sign is too low. How should it be fixed?"

👉 RESPONSE RULE:
Give:
1. What the issue is
2. Relevant IRC clause
3. Step-by-step fix
4. Placement/height rules (only if present)
Limit to 200 words.

-----------------------------------------------------
⚠ If insufficient info in context → answer exactly: "Not available."
-----------------------------------------------------

Now produce the best possible answer:
"""



    def answer(self, query: str):
        retrieved = self.retriever.retrieve(query, top_k=2)
        context = self.build_context(retrieved)
        prompt = self.build_prompt(query, context)
        answer = self.llm.generate(prompt)
        return answer, retrieved


# -----------------------------
# CLI interface
# -----------------------------

def main():
    print("==============================================")
    print("      Road Issue Assistant (RAG + Groq)")
    print("==============================================")

    db_path = os.path.join("data", "road_issues_example.json")
    pipeline = RoadRAGPipeline(db_path)

    while True:
        query = input("\nDescribe the road issue: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not query:
            print("Please enter a description (or 'exit' to quit).")
            continue

        print("\n[INFO] Processing...")
        answer, docs = pipeline.answer(query)

        print("\n======= AI SOLUTION =======\n")
        print(answer)

        print("\n======= DOCUMENTS USED =======")
        for i, (issue, score) in enumerate(docs, start=1):
            print(f"\nDoc {i} (Score: {score:.3f})")
            print(f"  Problem : {issue.problem}")
            print(f"  Category: {issue.category}")
            print(f"  Type    : {issue.type}")
            print(f"  Code    : {issue.code}")
            print(f"  Clause  : {issue.clause}")


if __name__ == "__main__":
    main()
