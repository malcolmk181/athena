"""
embedding_handling.py

Contains functions for creating and retrieving embeddings for note chunks.
"""

import uuid

import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document, HumanMessage, SystemMessage
from langchain.text_splitter import CharacterTextSplitter
from tqdm import tqdm

import file_handling
from load_environment import load_environment


CHUNK_SIZE = 1024
CHUNK_OVERLAP = 24


load_environment()


def get_embeddings_model() -> OpenAIEmbeddings:
    """Returns a LangChain OpenAIEmbeddings model."""

    return OpenAIEmbeddings(model="text-embedding-ada-002")


def get_vector_store_collection() -> chromadb.Collection:
    """Returns a client connection to the collection in the vector store. Creates both
    the vector store and the collection if they do not exist.
    """

    client = chromadb.PersistentClient(path="./.chromadb/")
    collection = client.get_or_create_collection(
        name="athena",
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def delete_vector_store_collection(are_you_sure: bool) -> None:
    """Deletes the vector store collection if it exists."""

    if are_you_sure:
        try:
            client = chromadb.PersistentClient(path="./.chromadb/")
            client.delete_collection("athena")

            print("Athena collection deleted.")

        except ValueError:
            print("Athena collection did not exist, nothing to delete.")


def get_chunks_from_file_name(file_name: str) -> tuple[Document, list[Document]]:
    """Returns a 2-tuple containing the original Document, and a list of its chunks as
    Documents.
    """

    loader = UnstructuredMarkdownLoader(f"../../../../{file_name}")

    chunks = loader.load_and_split(
        CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    )

    doc = loader.load()[0]

    return doc, chunks


def get_embedding_from_text(text: str) -> list[float]:
    """Returns the embeddings for a single text."""

    return get_embeddings_model().embed_documents([text])[0]


def save_note_embeddings_to_vector_store() -> None:
    """Create the embeddings for the notes in the vault and save them to the vector
    store. Creates the vector store if it does not exist.

    Also creates the note file store if it does not exist.
    """

    if not file_handling.file_store_exists():
        file_handling.create_new_note_store()

    file_store = file_handling.load_file_store()

    if not isinstance(file_store, dict):
        print("Loading file store failed. Embedding creation skipped.")
        return

    collection = get_vector_store_collection()

    for file_name in tqdm(file_store, desc="Notes", total=len(file_store)):
        if len(file_store[file_name]["chunks"]) == 0:
            _, chunks = get_chunks_from_file_name(file_name)

            file_store[file_name]["chunk_size"] = CHUNK_SIZE
            file_store[file_name]["chunk_overlap"] = CHUNK_OVERLAP

            for chunk in tqdm(chunks, desc="Chunks in note", total=len(chunks)):
                chunk_uuid = str(uuid.uuid4())

                file_store[file_name]["chunks"].append(chunk_uuid)

                chunk_embedding = get_embedding_from_text(chunk.page_content)

                collection.add(
                    ids=[chunk_uuid],
                    embeddings=[chunk_embedding],
                    metadatas=[{"document_uuid": file_store[file_name]["uuid"]}],
                    documents=[chunk.page_content],
                )

    file_handling.update_file_store(file_store)


def user_query_to_chromadb_query_result(query: str) -> chromadb.QueryResult:
    """
    Given a user's query, converts it into a declarative statement, then creates a set
    of embeddings for it, then queries the vector store collection for the most similar
    embeddings for the stored document chunks.
    """

    messages = [
        SystemMessage(
            content="You are a helpful assistant that converts user queries into declarative statements for the purposes of document retrieval using embedding cosine similarity."
        ),
        HumanMessage(
            content=f"Please convert the following user query into a declarative statement for document retrieval purposes. Focus on capturing the main topic and specific inquiry of the user's question. User's Question: {query}"
        ),
    ]

    declarative_query = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")(messages)

    embedding = get_embedding_from_text(declarative_query.content)

    return get_vector_store_collection().query([embedding])


def chroma_query_result_to_chunk_ids(
    query_result: chromadb.QueryResult,
    similarity_cutoff: float = 0.2,
    doc_limit: int = 10,
) -> list[str]:
    """
    Given a chromadb QueryResult, return a list of chunk ids from the most relevant
    documents that are within the cosine similarity difference of the cutoff.
    """

    results: list[str] = []

    for i, distance in enumerate(query_result["distances"][0]):
        if distance > similarity_cutoff or i > doc_limit - 1:
            break

        results.append(query_result["ids"][0][i])

    return results
