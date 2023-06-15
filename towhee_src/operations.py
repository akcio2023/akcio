import sys
import os
from typing import List
import logging

from towhee import AutoPipes

sys.path.append(os.path.dirname(__file__))

from store import DocStore, MemoryStore


logger = logging.getLogger(__name__)


doc_store = DocStore()
memory_store = MemoryStore()

# Initiate pipelines
insert_pipeline = AutoPipes.pipeline('osschat-insert', config=doc_store.insert_config)
search_pipeline = AutoPipes.pipeline('osschat-search', config=doc_store.search_config)


def chat(session_id, project, question):
    '''Chat API'''
    history = []
    # history = memory_store.get_history(project, session_id)
    res = search_pipeline(question, history, project)
    final_answer = res.get()[0]

    # Update history
    # messages = [{'question': question, 'answer': final_answer}]
    # memory_store.add_history(project, session_id, messages)
    return final_answer


def insert(data_src, project, source_type: str = 'file'):
    '''Load project docs will load docs from data source and then insert doc embeddings into the project table in the vector store.
    If there is no project table, it will create one.
    '''
    if not doc_store.has_project(project):
        doc_store.create_project(project)
    res = insert_pipeline(data_src, project).to_list()
    num = doc_store.count_entities(project)
    return num


def drop(project):
    '''Drop project will clean both vector and memory stores.'''
    # Clear vector db
    try:
        doc_store.drop(project)
    except Exception as e:
        logger.error('Failed to drop project:\n%s', e)
        raise RuntimeError from e
    # Clear memory
    try:
        memory_store.drop(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


def check(project):
    '''Check existences of project tables in both vector and memory stores.'''
    try:
        doc_check = doc_store.has_project(project)
    except Exception as e:
        logger.error('Failed to check table in vector db:\n%s', e)
        raise RuntimeError from e
    # Check memory
    try:
        memory_check = memory_store.check(project)
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e
    return {'store': doc_check, 'memory': memory_check}


def get_history(project, session_id):
    '''Get conversation history from memory store.'''
    try:
        messages = memory_store.get_history(project, session_id)
        return messages
    except Exception as e:
        logger.error('Failed to clean memory for the project:\n%s', e)
        raise RuntimeError from e


if __name__ == '__main__':
    project = 'akcio'
    data_src = 'https://docs.towhee.io/Triton%20Server/triton/'
    session_id = 'test000'
    question = 'How to debug pipeline in triton?'

    count = insert(data_src=data_src, project=project, source_type='url')
    print('Count:', count)
    print('Check:', check(project))

    answer = chat(project=project, session_id=session_id, question=question)
    print('Answer:', answer)
    print('Check:', check(project))
    print('History:', get_history(project, session_id))

    drop(project=project)
    print(check(project))
