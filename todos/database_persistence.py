import os
import psycopg2
import logging
from psycopg2.extras import DictCursor
from textwrap import dedent

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class DatabasePersistence:
    def __init__(self):
        if os.environ.get('FLASK_ENV') == 'production':
            dbname = os.environ.get('DATABASE_URL')
        else:
            dbname = 'todos'

        self.connection = psycopg2.connect(dbname=dbname)

        self._setup_schema()

    def create_new_list(self, title):
        # Adding with self.connection because it auto handles the transaction
        with self.connection:
            with self.connection.cursor() as cursor:
                query = dedent("""
                    INSERT INTO lists (title)
                    VALUES (%s)
                    """)
                cursor.execute(query,(title,))
                logger.info("Executing query: %s with title: %s", query, title)

    def update_list_by_id(self, list_id, new_title):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = """
                    UPDATE lists
                    SET title = %s
                    WHERE id = %s
                    """
                cursor.execute(query, (new_title, list_id))
                logger.info("Executing query: %s with new_title: %s and id: %s",
                        query, new_title, list_id)

    def delete_list(self, list_id):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = """
                    DELETE FROM lists
                    WHERE id = %s
                    """
                cursor.execute(query, (list_id, ))
                logger.info("Executing query: %s with list_id: %s", query, list_id)

    def all_lists(self):
        with self.connection:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                query = dedent("""
                    SELECT *
                    FROM lists
                    """)
                cursor.execute(query)
                logger.info("Executing query: %s", query)
                results = cursor.fetchall()
                lists = [dict(row) for row in results]

                for lst in lists:
                    todos = self._find_todos_for_list(lst['id'])
                    lst.setdefault('todos', todos)

                return lists

    def _find_todos_for_list(self, list_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = dedent(
                """
                SELECT *
                FROM todos
                WHERE list_id = %s
                """
            )
            cursor.execute(query, (list_id, ))
            logger.info("Executing query: %s with list_id: %s", query, list_id)

            todos = cursor.fetchall()
            return todos


    def find_list(self, list_id):
        with self.connection.cursor(cursor_factory=DictCursor) as cursor:
            query = dedent("""
                SELECT *
                FROM lists
                WHERE id = %s
                """)
            cursor.execute(query, (list_id, ))
            logger.info("Executing query: %s with list_id: %s", query, list_id)

            lst = dict(cursor.fetchone())
            todos = self._find_todos_for_list(list_id)
            lst.setdefault('todos', todos)
            return lst

    def create_new_todo(self, list_id, todo_title):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = dedent(
                    """
                    INSERT INTO todos(title, list_id)
                    VALUES (%s, %s)
                    """
                )
                cursor.execute(query, (todo_title, list_id))
                logger.info('Executed query: %s with title: %s and list_id: %s',
                            query, todo_title, list_id)

    def delete_todo_from_list(self, list_id, todo_id):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = dedent(
                    """
                    DELETE FROM todos
                    WHERE id = %s AND list_id = %s
                    """
                )
                cursor.execute(query, (todo_id, list_id))
                logger.info('Executed query: %s with todo_id: %s and list_id = %s',
                            query, todo_id, list_id)

    def find_todo(self, list_id, todo_id):
        with self.connection.cursor() as cursor:
            query = dedent(
                    """
                    SELECT * FROM todos
                    WHERE id = %s AND list_id = %s
                    """
            )
            cursor.execute(query, (todo_id, list_id))
            logger.info('Executed query: %s with todo_id: %s and list_id = %s',
                            query, todo_id, list_id)
            return cursor.fetchone()

    def update_todo_status(self, list_id, todo_id, completed):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = dedent(
                    """
                    UPDATE todos
                    SET completed = %s
                    WHERE id = %s AND list_id = %s
                    """
                )
                cursor.execute(query, (completed, todo_id, list_id))
                logger.info('Executed query: %s with completed status: %s, todo_id: %s, and list_id = %s',
                            query, completed, todo_id, list_id)

    def mark_all_todos_completed(self, list_id):
        with self.connection:
            with self.connection.cursor() as cursor:
                query = dedent(
                    """
                    UPDATE todos
                    SET completed = true
                    WHERE list_id = %s
                    """
                )
                cursor.execute(query, (list_id,))
                logger.info('Executed query: %s with list_id: %s',
                            query, list_id)

    def _setup_schema(self):
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'lists'
                    """
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        """
                        CREATE TABLE lists(
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL UNIQUE)
                        """
                    )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'todos'
                    """
                )
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        """
                        CREATE TABLE todos(
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        completed boolean NOT NULL DEFAULT false,
                        list_id INT NOT NULL
                                    REFERENCES lists(id)
                                    ON DELETE CASCADE)
                        """
                    )
