# Athena

This project is an exploration of using LLMs to both generate and retrieve from a knowledge graph to create an improved *Obsidian* Vault-informed chatbot. This project uses OpenAI's *GPT4* large language model to generate a *Neo4j* knowledge graph from the notes in a user's *Obsidian* Vault, as well as OpenAI's embedding model to store embeddings in a *ChromaDB* embedding store. The project uses both the knowledge graph and embedding store as sources of knowledge for answering user's questions.

For a significantly more thorough description of the project and the findings of it, please view the accompanying [Senior Project Final Report](https://drive.google.com/file/d/1BFFLO-k7-zlrsYIW4y1YYG5lxy0QBmJ3/view?usp=sharing), which goes into agonizing detail on how this project works.

## How to use

> [!WARNING]
> This is not a fully functional Obsidian plugin. It is wholly experimental in nature and not developed to the point of being easily used by someone else. Aside from the following missing features, this project also is not yet performant from a monetary or time perspective. I do not suggest trying to use this for personal use. The following key functionality for ease of use is missing:
> * An Obsidian UI
> * The ability to skip sending documents to OpenAI's API
> * The ability to easily update the embeddings store or knowledge graph on document changes
> * Configuration for which models to use
> * General error handling, including for API rate limiting
> * Confirmed functionality on Windows (macOS & Linux *should* work)

At this moment, there is no functional UI within Obsidian for answering questions. Questions can be answered by starting a FastAPI server and asking questions through its integrated Swagger page.

### Requirements

- [Obsidian](https://obsidian.md/), installed on Mac or Linux
- A funded OpenAI account and [API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key)
- [Neo4j Desktop](https://neo4j.com/download/)
- Python 3.10 or higher, and a variety of libraries
- [NodeJS](https://nodejs.org/en/download) v16 or higher

### Requirements Setup

*Plugin Setup*

- Clone this repo in your vault `VaultFolder/.obsidian/plugins/athena/`.
- Make sure your NodeJS is at least v16 (`node --version`).
- `npm i` or `yarn` to install dependencies.
- `npm run dev` to start compilation in watch mode.
  - After this runs, you can quit Node.js
- Open Obsidian and navigate to the settings pane. Open the `Community Plugins` tab.
- Enable the `Athena` plugin.
- Navigate to the new `Athena` tab at the bottom of the settings pane sidebar
- Enter your OpenAI API key in the corresponding settings box

*Neo4j Setup*

- Ensure that Neo4j desktop is installed.
- Create a new project to store your knowledge graph.
  - Within it, create a new Local DBMS and name it `athena`. Set the password to be `athena_password`.
  - Ensure the plugin `APOC` is installed into the DBMS

*Python Setup*

- Navigate to `VaultFolder/.obsidian/plugins/athena/python/`
- Create a new virtual environment with `python3 -m venv venv`
  - See the [Python documentation](https://docs.python.org/3/library/venv.html) for assistance with creating a virtual environment
- Activate the virtual environment using `source venv/bin/activate`
- Install the Python requirements using `pip install -r requirements.txt`

## Creating the knowledge graph & embeddings

In order to create the knowledge graph and embeddings, you'll need to start the Neo4j DB service and launch the FastAPI server and hit one of its endpoints.

Please note that the ability to easily update the embeddings and knowledge graph is not implemented. To update the embeddings and knowledge graph, the following `/build/` step must be ran again, which will delete all previously stored embeddings and knowledge graph.

- Open Neo4j Desktop and start the `athena` database service.
  - When you are done creating the knowledge graph or asking questions, be sure to stop this service to save resources on your computer.
- Navigate to `VaultFolder/.obsidian/plugins/athena/python/`
- Ensure the virtual environment is activated with `source venv/bin/activate`
- Run `uvicorn app:app --reload` to start the FastAPI server
  - Do not quit this process until you are completely done interacting with the project
- In your browser, navigate to `http://127.0.0.1:8000/docs`. This is the Swagger page where you can interact with the project.
- Open the `/build/` endpoint. Click "Try it out", then click "Execute". This will begin the building project.
  - Wait! This may take an incredibly long time, and will probably (at least partially) fail due to rate limits.
  - You'll know when the build process is as finished as it will get by pinging the `/ready/` endpoint. It will return `true` when it is done building.

## Asking Questions

Question answering is performed through the Swagger page. To answer questions, you'll need to make sure the Neo4j database is running, the FastAPI server is up, and the buid process finished.

- Start the Neo4j database service and FastAPI server using the instructions above
- Open the Swagger page at `http://127.0.0.1:8000/docs`
- Open the `/answer/` endpoint and click "Try it out".
- Type your question into the `question` box, and click "Execute".
  - Wait! This may take a few minutes to finish. In the meantime, you should be able to check the progress by observing the progress bar in the terminal where you started the FastAPI server.

## Notes

This project was completed in partial fulfillment of the CPSC 490 Senior Project requirement for a Bachelors of Science Degree in Computer Science at Yale University.

I named this project "Athena" after the Greek goddess. I developed this project while taking the course *An Introduction to Ancient Greek History* at Yale University, taught by the outstanding [Jessica Lamont](https://classics.yale.edu/people/jessica-lamont). It seemed appropriate while working on a project involving knowledge graphs, and knowledge management as a whole, to name my project after the Goddess of Wisdom, especially since much of my testing was done using notes I took during this course. Thank you Professor Lamont for a wonderful course, and content for my senior project!

Thank you to my advisor [Timos Antonopoulos](https://www.cs.yale.edu/homes/antonopoulos-timos/) for the continued support through the project :)

I'd like to mention the community Obsidian plugins [@exoascension/vault-chat](https://github.com/exoascension/vault-chat), [@longy2k/obsidian-bmo-chatbot](https://github.com/longy2k/obsidian-bmo-chatbot), and [@brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections) for serving as the primary inspirations behind making an Obsidian plugin. These projects are really cool and of a higher level than mine. I'd highly recommend checking them out for actual useable embeddings-based vault-aware RAG chatbots.

Lastly, a shoutout to [Tomaz Bratanic](https://medium.com/@bratanic-tomaz) of Neo4j. His Medium articles were instrumental in designing and implementing this project. The foundation for my graph creation code is adapted with little change from his article *[Constructing knowledge graphs from text using OpenAI functions](https://medium.com/@bratanic-tomaz/constructing-knowledge-graphs-from-text-using-openai-functions-096a6d010c17)*. Other articles of his were also incredibly helpful for understanding how to use LangChain with OpenAI's models and a Neo4j graph database.
