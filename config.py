import os

################## LLM ##################
chatllm_configs = {
    'model_name': 'gpt-3.5-turbo',
    'temperature': 0.8,
    'openai_api_key': os.getenv('OPENAI_API_KEY', 'your_openai_key_goes_here'),  # will use enviornment variable if not set in configs
    # 'openai_organization': ‘your_organization_goes_here’,  # will use enviornment variable if not set in configs
    # 'request_timeout': 600,  # in seconds
    # 'max_retries': 3,
    # 'streaming': False,
    # 'n': 1,
    # 'max_tokens': None
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
        'user': None,
        'password': None,
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