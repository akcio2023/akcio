# Towhee Pipelines

The `TowheePipeline` prepares insert and search pipeline for the system. It should have methods below to adapt operations in chatbot:

**`TowheePipeline`**

**Parameters:**

- `prompt_op`: the prompt operator used in search pipeline, defaults to `PROMPT_OP` from [prompt.py](./prompt.py). If it is None, it will use default prompts built in the search pipeline.

**Attributes:**

- `search_pipeline`: it searches relevant information across the project knowledge for the user's query, and then passes both user query and retrieved documents to LLM service to generate the final answer.
- `insert_pipeline`: it firstly loads & splits data from source (URL or file path), and then save documents & corresponding data such as text embeddings in database(s).

By default, it uses [Zilliz Cloud or Milvus](https://www.zilliz.com) to store documents with embeddings.
If scalar store is enabled, it will use [Elastic](https://www.elastic.co) as default scalar store.
You can modify [`config.py`](../../config.py) to configure it.

## Customization

- llm option: # todo
- prompts: modify [prompt.py](./prompt.py) to change system message and prompt template.
