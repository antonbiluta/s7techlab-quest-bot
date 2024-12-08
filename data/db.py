import sqlite3
from contextlib import closing

DB_PATH = "data/databases/questbot.db"


def initialize_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    team_name TEXT
                )
            ''')

            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS team_chats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            team_name TEXT UNIQUE,
                            chat_id INTEGER,
                            invite_link TEXT,
                            current_members INTEGER DEFAULT 0,
                            member_limit INTEGER
                        )
                    ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter_name TEXT UNIQUE,
                    is_work BOOLEAN DEFAULT 0,
                    params TEXT
                )
            ''')
            conn.commit()


def init_settings(param_name: str, is_work: bool, params: [str, None]):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            exists = cursor.execute('SELECT * FROM settings WHERE parameter_name = ?', (param_name,)).fetchone() is not None
            if not exists:
                cursor.execute('''
                    INSERT INTO settings (parameter_name, is_work, params) VALUES (?, ?, ?)
                ''', (param_name, is_work, params, param_name))


def get_settings_by_param_name(param_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE parameter_name = ?', (param_name,))
        return cursor.fetchone()


def add_chat(team_name: str, chat_id: int, member_limit: int, invite_link: str):
    status: bool = get_settings_by_param_name("get_default_members")[2]
    if get_chat_info_by_name(team_name):
        with closing(sqlite3.connect(DB_PATH)) as conn:
            with conn as cursor:
                if status:
                    cursor.execute('''
                        UPDATE team_chats
                        SET chat_id = ?, invite_link = ?, member_limit = ?
                        WHERE team_name = ?
                    ''', (chat_id, invite_link, member_limit, team_name))
                else:
                    cursor.execute('''
                    UPDATE team_chats 
                    SET chat_id = ?, invite_link = ? 
                    WHERE team_name = ?
                    ''', (chat_id, invite_link, team_name))
        return
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                INSERT INTO team_chats (team_name, chat_id, invite_link, member_limit)
                VALUES (?, ?, ?, ?)
            ''', (team_name, chat_id, invite_link, member_limit))


def update_chat(team_name: str, chat_id: int, member_limit: int, invite_link: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                INSERT INTO OR REPLACE team_chats (team_name, chat_id, invite_link, member_limit)
                VALUES (?, ?, ?, ?)
            ''', (team_name, chat_id, invite_link, member_limit))


def update_members(chat_id: int, increment: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                UPDATE team_chats
                SET current_members = current_members + ?
                WHERE chat_id = ?
            ''', (increment, chat_id))


def update_limit_by_name(team_name: str, new_limit: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                UPDATE team_chats
                SET member_limit = ?
                WHERE team_name = ?
            ''', (new_limit, team_name))


def update_link(team_name: str, invite_link: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                UPDATE team_chats
                SET invite_link = ?
                WHERE team_name = ?
            ''', (invite_link, team_name))


def get_chat_info_by_name(team_name: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM team_chats WHERE team_name = ?', (team_name,))
        return cursor.fetchone()


def get_chat_info(chat_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM team_chats WHERE chat_id = ?', (chat_id,))
        return cursor.fetchone()


def get_all_chats():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM team_chats')
        return cursor.fetchall()


def add_user(user_id: int, username: str, team_name: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO users (id, username, team_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, team_name))


def get_user(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()


def get_user_by_username(username: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()


def reset_user(user_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn as cursor:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))


def get_all_users():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()
