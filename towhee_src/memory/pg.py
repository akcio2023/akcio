import sys
import os
import json
from typing import List

import psycopg
from psycopg.rows import dict_row

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import memorydb_config
from base import BaseMemory

        
class MemoryStore(BaseMemory):
    def __init__(self):
        '''Initialize memory storage'''
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
