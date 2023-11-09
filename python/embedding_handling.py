"""
embedding_handling.py

Contains functions for creating and retrieving embeddings for note chunks.
"""

import uuid

import chromadb
from dotenv import load_dotenv
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from tqdm import tqdm

import file_handling


CHUNK_SIZE = 512
CHUNK_OVERLAP = 24


load_dotenv()


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


def get_chunks_from_file_name(file_name: str) -> list[Document]:
    loader = UnstructuredMarkdownLoader(f"../../../../{file_name}")

    return loader.load_and_split(
        CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    )


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
    embedding_model = get_embeddings_model()

    for file_name in tqdm(file_store, desc="Notes", total=len(file_store)):
        chunks = get_chunks_from_file_name(file_name)

        file_store[file_name]["chunk_size"] = CHUNK_SIZE
        file_store[file_name]["chunk_overlap"] = CHUNK_OVERLAP

        for chunk in tqdm(chunks, desc="Chunks in note", total=len(chunks)):
            chunk_uuid = str(uuid.uuid4())

            file_store[file_name]["chunks"].append(chunk_uuid)

            chunk_embedding = embedding_model.embed_documents([chunk.page_content])

            collection.add(
                ids=[chunk_uuid],
                embeddings=chunk_embedding,
                metadatas=[{"document_uuid": file_store[file_name]["uuid"]}],
                documents=[file_name],
            )

    file_handling.update_file_store(file_store)
