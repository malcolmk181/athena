"""
app.py

FastAPI server that exposes three endpoints:
    - /answer/ : Given a user's question, returns the answer.
    - /build/ : Builds the knowledge graph and embeddings from scratch.
    - /ready/ : Checks if the knowledge graph and embeddings are ready to be queried.

This file is meant to be run as a server. To run it, use the following command:
    uvicorn app:app --reload

To access the server from the browser, go to http://127.0.0.1:8000/docs
"""

import os

from fastapi import BackgroundTasks, FastAPI

from ask_questions import answer_question
from build_kg_and_embeddings import build_kg_and_embeddings

app = FastAPI()


@app.get("/answer/")
async def answer(question: str):
    """
    Given a user's question, calls the KG & embedding querying code and returns the
    answer.
    """

    try:
        result = answer_question(question)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


@app.post("/build/")
async def build(background_tasks: BackgroundTasks):
    """Builds the knowledge graph and embeddings from scratch."""

    background_tasks.add_task(build_kg_and_embeddings)
    return {"message": "Knowledge graph and embeddings are being built."}


@app.get("/ready/")
async def ready():
    """Checks if the knowledge graph and embeddings are ready to be queried."""

    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "done_generating")

    if os.path.exists(file_path):
        return {"ready": True}

    return {"ready": False}
