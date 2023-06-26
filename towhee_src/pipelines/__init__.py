import sys
import os
from typing import Any

from pymilvus import connections, Collection
from towhee import AutoConfig, AutoPipes

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import (
    USE_SCALAR,
    textencoder_config, chatllm_configs,
    vectordb_config, scalardb_config
    )
from towhee_src.pipelines.prompt import PROMPT_OP


class TowheePipelines:
    def __init__(self, prompt_op: Any = PROMPT_OP):
        self.prompt_op = prompt_op
        self.milvus_uri = vectordb_config['connection_args']['uri']
        self.milvus_host = self.milvus_uri.split('https://')[1].split(':')[0]
        self.milvus_port = self.milvus_uri.split('https://')[1].split(':')[1]
        milvus_user = vectordb_config['connection_args']['user']
        self.milvus_user = None if milvus_user == '' else milvus_user
        milvus_password = vectordb_config['connection_args']['password']
        self.milvus_password = None if milvus_password == '' else milvus_password

        connections.connect(
            host=self.milvus_host,
            port=self.milvus_port,
            user=self.milvus_user,
            password=self.milvus_password
        )

        if USE_SCALAR:
            from elasticsearch import Elasticsearch

            self.es_uri = scalardb_config['connection_args']['hosts']
            self.es_host = self.es_uri.split('https://')[1].split(':')[0]
            self.es_port= self.es_uri.split('https://')[1].split(':')[1]
            self.es_ca_certs = scalardb_config['connection_args']['ca_certs']
            self.es_basic_auth = scalardb_config['connection_args']['basic_auth']
            self.es_user = self.es_basic_auth[0]
            self.es_password = self.es_basic_auth[1]
            self.es_client = Elasticsearch(
                self.es_uri,
                ca_certs=self.es_ca_certs,
                basic_auth=self.es_basic_auth
                )

    @property
    def search_pipeline(self):
        search_pipeline = AutoPipes.pipeline('osschat-search', config=self.search_config)
        return search_pipeline

    @property
    def insert_pipeline(self):
        insert_pipeline = AutoPipes.pipeline('osschat-insert', config=self.insert_config)
        return insert_pipeline

    @property
    def search_config(self):
        search_config = AutoConfig.load_config('osschat-search')
        
        # Configure embedding
        search_config.embedding_model = textencoder_config['model']
        search_config.embedding_normalize = textencoder_config['norm']

        # Configure LLM
        search_config.llm_src = 'openai'
        search_config.openai_api_key = chatllm_configs['openai_api_key']
        
        if self.prompt_op:
            search_config.customize_prompt = self.prompt_op

        # Configure vector store (Milvus/Zilliz)
        search_config.milvus_host = self.milvus_host
        search_config.milvus_port = self.milvus_port
        search_config.milvus_user = self.milvus_user
        search_config.milvus_password = self.milvus_password
        search_config.milvus_top_k = vectordb_config['top_k']
        search_config.threshold = vectordb_config['threshold']
        
        # Configure scalar store (ES)
        if USE_SCALAR:
            search_config.es_enable = True
            search_config.es_host = self.es_host
            search_config.es_port = self.es_port
            search_config.es_user = self.es_user
            search_config.es_password = self.es_password
            search_config.es_ca_certs = self.es_ca_certs
        else:
            search_config.es_enable = False
        return search_config
    
    @property
    def insert_config(self):
        insert_config = AutoConfig.load_config('osschat-insert')

        # Configure embedding
        insert_config.embedding_model = textencoder_config['model']
        insert_config.embedding_normalize = textencoder_config['norm']

        # Configure vector store (Milvus/Zilliz)
        insert_config.milvus_host = self.milvus_host
        insert_config.milvus_port = self.milvus_port
        insert_config.milvus_user = self.milvus_user
        insert_config.milvus_password = self.milvus_password

        # Configure scalar store (ES)
        if USE_SCALAR:
            insert_config.es_enable = True
            insert_config.es_host = self.es_host
            insert_config.es_port = self.es_port
            insert_config.es_user = self.es_user
            insert_config.es_password = self.es_password
            insert_config.es_ca_certs = self.es_ca_certs
        else:
            insert_config.es_enable = False
        return insert_config
    
    def create_project(self, project: str):
        from pymilvus import CollectionSchema, FieldSchema, DataType

        fields = [
            FieldSchema(name='id', dtype=DataType.INT64, description='ids', is_primary=True, auto_id=True),
            FieldSchema(name='text_id', dtype=DataType.VARCHAR, description='text', max_length=500),
            FieldSchema(name='text', dtype=DataType.VARCHAR, description='text', max_length=1000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, description='embedding vectors', dim=textencoder_config['dim'])
            ]
        schema = CollectionSchema(fields=fields, description='osschat')
        collection = Collection(name=project, schema=schema)

        index_params = vectordb_config['index_params']
        collection.create_index(field_name="embedding", index_params=index_params)
        return collection

    def drop(self, project):
        assert self.has_project(project), f'No project store: {project}'
        # drop vector store
        collection = Collection(project)
        collection.drop()

        if USE_SCALAR:
            # drop scalar store
            self.es_client.indices.delete(index=project)

        assert not self.has_project(project), f'Failed to drop project store : {project}'

    def has_project(self, project):
        from pymilvus import utility

        status = utility.has_collection(project) # check vector store
        if USE_SCALAR:
            assert self.es_client.indices.exists(index=project) == status # check scalar store
        return status
    
    def count_entities(self, project):
        collection = Collection(project)
        collection.flush()
        milvus_count = collection.num_entities
        if USE_SCALAR:
            es_count = self.es_client.count(index=project)['count']
            assert es_count == milvus_count, 'Mismatched data count in Milvus vs Elastic.'
        return milvus_count