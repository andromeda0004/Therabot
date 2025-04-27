import sqlite3
import click
import os
from flask import current_app, g

# g is a special object unique for each request. Used to store data during a request context.
# current_app is another special object pointing to the Flask app handling the request.

def get_db():
    """Connect to the application's configured database. Cache the connection on 'g'."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        print(f"Database connection established for request {id(g)}.")
    return g.db

def close_db(e=None):
    """Close the database connection if it was opened."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        print(f"Database connection closed for request {id(g)}.")

def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    # Read schema from a file (good practice)
    # Assuming you have a 'schema.sql' file next to this db.py
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    try:
        with current_app.open_resource(schema_path) as f:
             # Ensure correct decoding if schema.sql uses non-ASCII characters
            db.executescript(f.read().decode('utf8'))
        print("Database schema executed.")
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}. Creating default table.")
        # Fallback to inline SQL if schema file is missing (less ideal)
        db.execute('''
            DROP TABLE IF EXISTS users;
        ''')
        db.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        print("Default 'users' table created.")
    except Exception as e:
        print(f"Error executing schema: {e}")


@click.command('init-db')
def init_db_command():
    """CLI command to initialize the database."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    # Tell Flask to call close_db when cleaning up after returning the response
    app.teardown_appcontext(close_db)
    # Add the new command to be called with the 'flask' command
    app.cli.add_command(init_db_command)