import sys
import os
import json
from typing import List

import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config import memorydb_config
from base import MemoryStore

        
class MemoryStore(MemoryStore):
    def __init__(self,
                 db_name: str = MEMORY_DB,
                 table_name: str = MEMORY_TABLE
                 ):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.table_name = table_name

    def add_history(self, session_id: str, messages: List[dict]):
        self._create_table_if_not_exists()
        query = f'INSERT INTO {self.table_name} (session_id, message) VALUES (?, ?);'
        for message in messages:
            data=json.dumps(self._message_to_dict(message))
            self.cursor.execute(query, (session_id, data,))
            self.connection.commit()

    def get_history(self, session_id: str):
        if self.check():
            query = f'SELECT message FROM {self.table_name} WHERE session_id = "{session_id}" ;'
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            messages = [self._message_from_dict(json.loads(i[0])) for i in res]
        else:
            messages = []
        return messages

    def _create_table_if_not_exists(self):
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INT PRIMARY KEY,
            session_id TEXT NOT NULL,
            message TEXT NOT NULL
        );'''
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def clear(self, session_id: str = None):
        assert self.check(), f'Memory does not exist: {self.table_name}.'
        if session_id:
            query = f'DELETE FROM {self.table_name} WHERE session_id = "{session_id}";'
            self.cursor.execute(query)
        else:
            query = f'DROP TABLE {self.table_name};'
            self.cursor.execute(query)
        self.connection.commit()

    def check(self):
        check = f'SELECT name FROM sqlite_master WHERE type="table" AND name="{self.table_name}";'
        # check = f'SELECT COUNT(*) FROM  WHERE relname = {self.table_name};'
        self.cursor.execute(check)
        record = self.cursor.fetchone()
        return bool(record)
    
    @staticmethod
    def _message_from_dict(message: dict):
        return message['data']
    
    @staticmethod
    def _message_to_dict(message: dict) -> dict:
        return {'type': 'chat', 'data': message}
    