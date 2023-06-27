# Akcio: Enhancing LLM-Powered ChatBot with CVP Stack

[OSSChat](https://osschat.io) |
[Documentation](https://github.com/akcio2023/akcio/wiki) |
[Contact](https://zilliz.com/contact-sales) |
[ToS](./ToS.md)

Index

- [Overview](#overview)
- [Deployment](#deployment)
- [Load Data](#load-data)
- [Notice](#notice)

ChatGPT has constraints due to its limited knowledge base, sometimes resulting in hallucinating answers when asked about unfamiliar topics. We are introducing the new AI stack, ChatGPT+Vector database+prompt-as-code, or the CVP Stack, to overcome this constraint.

We have built [OSSChat](https://osschat.io) as a working demonstration of the CVP stack. Now we are presenting the technology behind OSSChat in this repository with a code name of Akcio.

<img src='pics/osschat_web.png' width='100%' alignment='centre'>

With this project, you are able to build a knowledge-enhanced ChatBot using LLM service like ChatGPT. 
By the end, you will learn how to start a backend service using FastAPI, which provides standby APIs to support further applications. Alternatively, we show how to use Gradio to build an online demo with user interface.

## Overview

<img src='pics/osschat.png' width='75%' alignment='centre'>

Akcio allows you to create a ChatGPT-like system with added intelligence obtained through semantic search of customized knowledge base.
Instead of sending the user query directly to LLM service, our system firstly retrieves relevant information from stores by semantic search or keyword match. Then it feeds both user needs and helpful information into LLM. This allows LLM to better tailor its response to the user's needs and provide more accurate and helpful information.

You can find more details and instructions at our [documentation](https://github.com/akcio2023/akcio/wiki).

Akcio offers two AI platforms to choose from: [Towhee](https://towhee.io) or [LangChain](https://langchain.com).

### Option 1: Towhee

The option using Towhee simplifies the process of building a system by providing [pre-defined pipelines](https://towhee.io/tasks/pipeline). These built-in pipelines require less coding and make system building much easier. If you require customization, you can either simply modify configuration or create your own pipeline with rich options of [Towhee Operators](https://towhee.io/tasks/operator).

- [Pipelines](./towhee_src/pipelines)
    - **Insert:** the insert pipeline builds a knowledge base by saving documents and corresponding data in database(s).
    - **Search:** the search pipeline enables the question-answering capability powered by information retrieval (semantic search and optional keyword match) and LLM service. 
    - **Prompt:** a prompt operator prepares messages for LLM by assembling system message, chat history, and the user's query processed by template.

- [Memory](./towhee_src/memory):
    The memory storage stores chat history to support context in conversation. (available: [Postgresql](./towhee_src/memory/pg.py))


### Option 2: LangChain

The option using LangChain employs the use of [Agent](https://python.langchain.com/docs/modules/agents) in order to enable LLM to utilize specific tools, resulting in a greater demand for LLM's ability to comprehend tasks and make informed decisions.

- [Agent](./langchain_src/agent)
    - **ChatAgent:** agent ensembles all modules together to build up qa system.
    - Other agents (todo)
- [LLM](./langchain_src/llm)
    - **ChatLLM:** large language model or service to generate answers (available: [OpenAI](langchain_src/llm/openai_chat.py), [Dolly](langchain_src/llm/dolly_chat.py), [Ernie](langchain_src/llm/ernie.py))
- [Embedding](./langchain_src/embedding/)
    - **TextEncoder:** encoder converts each text input to a vector (available: [OpenAI embedding](langchain_src/embedding/openai_embedding.py), [HuggingFace Hub](langchain_src/embedding/langchain_huggingface.py))
    - Other encoders (todo)
- [Store](./langchain_src/store)
    - **VectorStore:** vector database stores document chunks in embeddings, and performs document retrieval via semantic search. (available: [Milvus/Zilliz Cloud](langchain_src/store/vector_store/milvus.py))
    - **ScalarStore:** optional, database stores metadata for each document chunk, which supports additional information retrieval. (available: [Elastic](langchain_src/store/scalar_store/es.py))
    - **MemoryStore:** memory storage stores chat history to support context in conversation. (available: [Postgresql](langchain_src/store/memory_store/pg.py))
- [DataLoader](./langchain_src/data_loader/)
    - **DataParser:** tool loads data from given source and then splits documents into processed doc chunks.
    - **QuestionGenerator:** tool generates a list of potential questions for each document chunk.

## Deployment

1. Downloads
    ```shell
    $ git clone https://github.com/akcio2023/akcio.git
    $ cd akcio
    ```

2. Install dependencies
    ```shell
    $ pip install -r requirements.txt
    ```

3. Configure modules
    - Agent

        It will use default agents and prompts.
        If you want to configure prompts or customize agent modules, refer to [agent](./langchain_src/agent) for guide.

    - LLM

        The default ChatAI module uses OpenAI service, which requires an [OpenAI API key](https://platform.openai.com/account/api-keys).

        ```shell
        $ export OPENAI_API_KEY=your_keys_here
        ```

        If you want to customize llm modules, you can refer to [llm](./langchain_src/llm) for guide.
        
    - Embedding

        By default, the embedding module uses LangChain HuggingFaceEmbeddings to convert text inputs to vectors. Here are some information about the default embedding method:
        - model: [multi-qa-mpnet-base-cos-v1](https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-cos-v1)(420MB)
        - dim: 768
        - normalization: True

        If you want to customize embedding method, you can refer to [embedding](./langchain_src/embedding) for guide.

    - Store

        - Vector Store: You need to prepare the service of vector database in advance. For example, you can refer to [Milvus Documents](https://milvus.io/docs) or [Zilliz Cloud](https://zilliz.com/doc/quick_start) to learn about how to start a Milvus service.
        - Scalar Store (Optional): This is optional, only work when `USE_SCALAR` is true in [configuration](config.py). If this is enabled (i.e. USE_SCALAR=True), the default scalar store will use [Elastic](https://www.elastic.co/). In this case, you need to prepare the Elasticsearch service in advance.
        - Memory Store: You need to prepare the database for memory storage as well. By default, the memory store uses [Postgresql](https://www.postgresqltutorial.com) which much be running and be configured with a database and user and password with wriote and create access.

        The store will use default store configs.
        To set up your special connections for each database, you can export environment variables instead of modifying **config.py**.

        For the Vector Store, set **MILVUS_URI**:
        ```shell
        $ export MILVUS_URI=https://localhost:19530
        ```

       For the Memory Store, set **PG_URI** to **postgresql://{user}:{password}@{host}/{database_name}**:
        ```shell
        $ export PG_URI=postgresql://postgres:postgres@localhost/chat_history
        ```

        For advanced configurations for store services, you can modify the Store section in [config.py](config.py).

4. Start service

    The main script will run a FastAPI service with default address `localhost:8900`.

    - Option 1: LangChain
        ```shell
        $ python main.py --langchain
        ```
    - Option 2: Towhee
        ```shell
        $ python main.py --towhee
        ```

4. Access via browser
    
    You can open url https://localhost:8900/docs in browser to access the web service.

    <img src='pics/fastapi.png' width='75%' alignment='centre'>

    > `/`: Check service status
    >
    > `/answer`: Generate answer for the given question, with assigned session_id and project
    >
    > `/project/add`: Add data to project (will create the project if not exist)
    >
    > `/project/drop`: Drop project including delete data in both vector and memory storages.


## Load data

The `insert` function in [operations](./langchain_src/operations.py) loads project data from url(s) or file(s).

There are 2 options to load project data:

### Option 1: Offline

We recommend this method, which loads data in separate steps.
There is also advanced options to load document with advanced options.
Refer to [offline_tools](./langchain_src/offline_tools) for instructions.

### Option 2. Online

When the [FastAPI service](#deployment) is up, you can use the POST request `http://localhost:8900/project/add` to load data.

Parameters:
```json
{
  "project": "project_name",
  "data_src": "path_to_doc",
  "source_type": "file"
}
```
or
```json
{
  "project": "project_name",
  "data_src": "doc_url",
  "source_type": "url"
}
```

This method is only recommended to load a small amount of data, but **not for a large amount of data**.


<br />

---

## Notice
Akcio is a project developed by Zilliz, All rights reserved. 

By using our project or any part of our project, you agree to the [Terms of Service](./ToS.md).
