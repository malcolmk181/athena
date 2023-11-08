"""
graph_handling.py

Contains functions for creating graphs and pulling information from them.
"""

from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph


load_dotenv()
# OPENAI_API_KEY in .env file


NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "athena_password"


def get_graph() -> Neo4jGraph:
    """Returns a wrapper for the Neo4j database."""

    return Neo4jGraph(
        url=NEO4J_URL,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
    )
