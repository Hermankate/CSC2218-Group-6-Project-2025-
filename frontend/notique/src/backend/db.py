import sqlite3
from contextlib import closing

DATABASE_NAME = "notes.db"

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create notes table with foreign key constraint
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster user-based queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_user ON notes(user_id)
        ''')
        
        conn.commit()

def add_user(name, email):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Email {email} already exists")
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

def get_user_by_email(email):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, created_at FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        if user:
            return {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "created_at": user[3]
            }
        return None

def add_note(user_id, title, content):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO notes (user_id, title, content)
                VALUES (?, ?, ?)""",
                (user_id, title, content)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to add note: {str(e)}")

def get_notes(user_id):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, title, content, timestamp 
            FROM notes WHERE user_id = ? 
            ORDER BY timestamp DESC""",
            (user_id,)
        )
        return [
            {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "timestamp": row[3]
            }
            for row in cursor.fetchall()
        ]

def update_note(note_id, title, content):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE notes SET title = ?, content = ? WHERE id = ?",
                (title, content, note_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to update note: {str(e)}")

def delete_note(note_id):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM notes WHERE id = ?",
                (note_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to delete note: {str(e)}")

def get_note_by_id(note_id):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id, title, content, timestamp 
            FROM notes WHERE id = ?""",
            (note_id,)
        )
        note = cursor.fetchone()
        if note:
            return {
                "id": note[0],
                "user_id": note[1],
                "title": note[2],
                "content": note[3],
                "timestamp": note[4]
            }
        return None