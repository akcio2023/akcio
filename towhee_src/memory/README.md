# Memory

The `MemoryStore` records chat history in database. It should have methods below to adapt operations in chatbot:

**`MemoryStore`**

**Methods:**

- `add_history`: insert chat history to database, given a list of dictionaries with keys of 'question' and 'answer', [{'question': 'xxx', 'answer': 'xxx'}]
- `get_history`: return chat history in a list of tuples, [('this is question', 'this is answer')]

By default, it uses [Postgresql](https://www.postgresql.org/) to manage memory. You can modify [`config.py`](../../config.py) to configure it.

## Customization

To manage memory with some other database, you can import your own MemoryStore in [__init__.py](./__init__.py).
For example, changing `.pg` to `.sqlite` in the init file will switch to sqlite.
In the meantime, don't forget to modify [config.py](../../config.py) for a changed `memorydb_config`.
You can follow instructions below to customize the module:

```python
from typing import List
from config import memorydb_config

        
class MemoryStore:
    def __init__(self):
        '''Initialize memory storage, eg. connect to your database'''
        pass

    def add_history(self, project: str, session_id: str, messages: List[dict]):
        '''Insert messages to the project table with a field of session_id.'''
        pass

    def get_history(self, project: str, session_id: str) -> List[tuple]:
        '''Get chat history from the project table for each session.'''

    def drop(self, project):
        '''Clear all memory saved in the table "project"'''

    def check(self, project) -> bool:
        '''Check if the project table exists in database.'''
```
