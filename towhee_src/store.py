import sys
import os
import json
from typing import Optional, List

import psycopg  # pylint: disable=C0415
from psycopg.rows import dict_row  # pylint: disable=C0415
from pymilvus import connections, Collection
from towhee import AutoConfig

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import (
    USE_SCALAR,
    textencoder_config, chatllm_configs,
    vectordb_config, scalardb_config, memorydb_config
    )


class DocStore:
    def __init__(self):
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


    def search(self, project: str, query: str):
        # todo
        pass

    def insert(self, project: str, data: List[str], metadatas: Optional[List[dict]] = None):
        # todo
        pass

    def insert_embeddings(self, data: List[float], metadatas: List[dict]):
        # todo
        pass

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

    @property
    def search_config(self):
        search_config = AutoConfig.load_config('osschat-search')
        
        # Configure embedding
        search_config.embedding_model = textencoder_config['model']
        search_config.embedding_normalize = textencoder_config['norm']

        # Configure LLM
        search_config.llm_src = 'openai'
        search_config.openai_api_key = chatllm_configs['openai_api_key']

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
        
class MemoryStore:
    def __init__(self):
        '''Initialize memory storage: e.g. history_db'''
        self.connection = psycopg.connect(memorydb_config['connect_str'])
        self.cursor = self.connection.cursor(row_factory=dict_row)

    def add_history(self, project: str, session_id: str, messages: List[dict]):
        from psycopg import sql

        self._create_table_if_not_exists(project)

        query = sql.SQL("INSERT INTO {} (session_id, message) VALUES (%s, %s);").format(
            sql.Identifier(project)
        )
        for message in messages:
            self.cursor.execute(
                query, (session_id, json.dumps(self._message_to_dict(message)))
            )
            self.connection.commit()

    def get_history(self, project: str, session_id: str):
        if self.check(project):
            query = f"SELECT message FROM {project} WHERE session_id = %s ;"
            self.cursor.execute(query, (session_id,))
            items = [record["message"] for record in self.cursor.fetchall()]
            messages = [self._message_from_dict(i) for i in items]
        else:
            messages = []
        return messages

    def _create_table_if_not_exists(self, project):
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {project} (
            id SERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            message JSONB NOT NULL
        );'''
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def drop(self, project):
        existence = self.check(project)
        query = f'DROP TABLE {project};'
        self.cursor.execute(query)
        self.connection.commit()

        existence = self.check(project)
        assert not existence, f'Failed to drop table {project}.'

    def check(self, project):
        check = 'SELECT COUNT(*) FROM pg_class WHERE relname = %s;'
        self.cursor.execute(check, (project,))
        record = self.cursor.fetchall()
        return bool(record[0]['count'] > 0)
    
    @staticmethod
    def _message_from_dict(message: dict):
        return tuple(message['data'])
    
    @staticmethod
    def _message_to_dict(message: tuple) -> dict:
        return {'type': 'chat', 'data': message}
