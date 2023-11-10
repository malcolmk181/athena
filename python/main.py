from tqdm import tqdm

import embedding_handling
import file_handling
import graph_handling


def main() -> None:
    """Creates a new file store, embedding vector store, and graph."""

    graph = graph_handling.get_graph_connector()

    # wipe the slate clean
    graph_handling.delete_graph(True)
    file_handling.create_new_note_store(True)
    embedding_handling.delete_vector_store_collection(True)

    # Rebuild the vector store and file store
    embedding_handling.save_note_embeddings_to_vector_store()

    note_file_names = file_handling.collect_files_from_vault()

    # Rebuild the graph
    for note in tqdm(
        note_file_names,
        desc="Creating graph & embedding for each note in vault.",
        total=len(note_file_names),
    ):
        graph_doc = graph_handling.create_graph_document_from_note(
            note, graph_handling.GPT4
        )
        graph.add_graph_documents([graph_doc])


if __name__ == "__main__":
    main()
