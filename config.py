import os

################## LLM ##################
chat_configs = {
    'openai': {
        'openai_model': 'gpt-3.5-turbo',
        'openai_api_key': None,  # will use environment  value 'OPENAI_API_KEY' if None
        'llm_kwargs': {
            'temperature': 0.8,
            # 'max_tokens': 200,
            }
    },
    'ernie': {
        'ernie_api_key': None, # If None, use environment  value 'ERNIE_API_KEY'
        'ernie_secret_key': None, # If None, use environment value 'ERNIE_SECRET_KEY'
        'llm_kwargs': {}
    },
    'minimax': {
        'minimax_model': 'abab5-chat',
        'minimax_api_key': None, # If None, use environment value 'MINIMAX_API_KEY'
        'minimax_group_id': None, # If None, use environment value 'MINIMAX_GROUP_ID'
        'llm_kwargs': {}
    },
    'dolly': {
        'dolly_model': 'databricks/dolly-v2-3b',
        'llm_kwargs': {'device': 'auto'}
    },
}


################## Embedding ##################
textencoder_config = {
    'model': 'multi-qa-mpnet-base-cos-v1',
    'norm': True,
    'dim': 768
}


################## Store ##################
USE_SCALAR = False

# Vector db configs
vectordb_config = {
    'connection_args': {
        'uri': os.getenv('MILVUS_URI', 'https://localhost:19530'),
        'user': os.getenv('MILVUS_USER', ''),
        'password': os.getenv('MILVUS_PASSWORD', ''),
        'secure': os.getenv('MILVUS_SECURE', False)
        },
    'top_k': 10,
    'threshold': 0.6,
    'index_params': {
        'metric_type': 'IP',
        'index_type': 'IVF_FLAT',
        'params': {'nlist': 1024}
        }
}

# Scalar db configs
scalardb_config = {
    'connection_args': {
        'hosts': os.getenv('ES_HOSTS', 'https://localhost:9200'),
        'ca_certs': os.getenv('ES_CA_CERTS', None),
        'basic_auth': (os.getenv('ES_USER', 'user_name'), os.getenv('ES_PASSWORD', 'es_password'))
        },
}

# Memory db configs
memorydb_config = {
    'connect_str': os.getenv('PG_URI', 'postgresql://postgres:postgres@localhost/chat_history')
}

################## Data loader ##################
dataparser_configs = {
    'chunk_size': 300
}

questiongenerator_configs = {
    'model_name': 'gpt-3.5-turbo',
    'temperature': 0,
}