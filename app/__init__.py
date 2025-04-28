from flask import Flask
from flask_login import LoginManager
import sqlite3
import os
import datetime

# Path for our SQLite database file - Use Flask's instance folder
DATABASE = 'therabot.db'  # Just the filename, Flask will use instance_path

# --- Define login_manager at the module level ---
login_manager = LoginManager()
login_manager.login_view = 'main.login'  # Correct login view endpoint
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

def create_app():
    # No instance_relative_config needed for purely local setup
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # --- Configuration ---
    # Keep configuration simple and directly in the code for local use
    app.config.from_mapping(
        # Use a simple, fixed secret key for local development.
        # IMPORTANT: DO NOT use this key if the app ever becomes public.
        SECRET_KEY='local-therabot-secret-key-dev',
        DATABASE=os.path.join(app.instance_path, DATABASE),
    )
    # Removed loading from instance/config.py

    # --- Extensions ---
    # Initialize login_manager with the app
    login_manager.init_app(app)

    # --- Database ---
    from . import db # Import database functions
    db.init_app(app) # Initialize database commands (like init-db)

    # --- User Loader ---
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        conn = db.get_db()
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user_data:
            return User(user_data['id'], user_data['username'], user_data['password'])
        return None

    # --- Blueprints ---
    from . import routes
    app.register_blueprint(routes.main)

    # --- Context Processors ---
    @app.context_processor
    def inject_current_year():
        # Ensure datetime is available
        try:
            # Use timezone aware datetime if possible, otherwise naive
            now = datetime.datetime.now(datetime.timezone.utc)
        except AttributeError: # Handle environments without timezone
            now = datetime.datetime.utcnow()
        except NameError:
            import datetime
            now = datetime.datetime.utcnow() # Fallback again
        return {'current_year': now.year}

    print(f"App created for LOCAL development.")
    print(f"Database path: {app.config['DATABASE']}")

    return app