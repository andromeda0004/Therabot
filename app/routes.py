import os
import json
import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request,
    session, url_for, jsonify, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from app import login_manager
from datetime import datetime
# Import the chatbot from emotion_chatbot.py
from emotion_chatbot import chatbot_respond

# Change bp to main to match what __init__.py expects
main = Blueprint('main', __name__)

@main.route('/')
def index():
    current_year = datetime.now().year
    return render_template('landing.html', current_year=current_year)

@main.route('/chat', methods=('GET', 'POST'))
@login_required
def chat():
    db = get_db()
    user_id = current_user.id
    username = current_user.username
    
    if request.method == 'POST':
        # For AJAX requests that send JSON
        if request.is_json:
            data = request.get_json()
            message = data.get('message', '').strip()
            user_mood = data.get('mood', None)  # Get the user's mood if provided
            hidden = data.get('hidden', False)  # Check if this is a hidden message (for mood updates)
            
            if not message:
                return jsonify({
                    'error': 'Message is required.'
                }), 400
            
            # Only save user message to chat history if it's not hidden
            if not hidden:
                db.execute(
                    'INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)',
                    (user_id, 'user', message)
                )
                db.commit()  # Add commit here to prevent database locks
            
            # Get bot response with mood context if provided
            if user_mood:
                bot_reply, detected_emotion, should_play_rain = chatbot_respond(message, user_id=user_id, user_mood=user_mood, username=username)
            else:
                bot_reply, detected_emotion, should_play_rain = chatbot_respond(message, user_id=user_id, username=username)
            
            # Only save bot response to chat history if it's not hidden
            if not hidden:
                db.execute(
                    'INSERT INTO chat_history (user_id, sender, message, emotion) VALUES (?, ?, ?, ?)',
                    (user_id, 'bot', bot_reply, detected_emotion)
                )
                db.commit()
            
            # Return JSON response for AJAX
            return jsonify({
                'bot_reply': bot_reply,
                'emotion': detected_emotion if user_mood is None else user_mood,
                'play_rain': should_play_rain  # Changed from should_play_rain to match frontend's expected parameter
            })
        
        # For regular form submissions
        else:
            message = request.form['message'].strip()
            if not message:
                flash('Message is required.', 'danger')
                return redirect(url_for('main.chat'))
            
            # Save user message to chat history
            db.execute(
                'INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)',
                (user_id, 'user', message)
            )
            db.commit()  # Add commit here to prevent database locks
            
            # Get bot response
            bot_reply, detected_emotion, should_play_rain = chatbot_respond(message, user_id=user_id, username=username)
            
            # Save bot response to chat history
            db.execute(
                'INSERT INTO chat_history (user_id, sender, message, emotion) VALUES (?, ?, ?, ?)',
                (user_id, 'bot', bot_reply, detected_emotion)
            )
            db.commit()
            
            return redirect(url_for('main.chat'))
    
    # --- GET Request Handling ---
    # Check if we need to show the mood modal
    show_modal = session.pop('show_mood_modal', False)
    
    # Fetch chat history for this user
    chat_history = db.execute(
        'SELECT * FROM chat_history WHERE user_id = ? ORDER BY timestamp',
        (user_id,)
    ).fetchall()
    
    # Create a list of dictionaries for easier template rendering
    chat_messages = []
    for msg in chat_history:
        chat_messages.append({
            'sender': msg['sender'],
            'message': msg['message'],
            'emotion': msg['emotion'],
            'timestamp': msg['timestamp']
        })
    
    # If there are no messages yet, generate an initial greeting
    if not chat_messages:
        greeting = f"Hello {username}! 👋 I'm Therabot, your mental health assistant. How are you feeling today? 😊"
        db.execute(
            'INSERT INTO chat_history (user_id, sender, message, emotion) VALUES (?, ?, ?, ?)',
            (user_id, 'bot', greeting, 'neutral')
        )
        db.commit()
        
        chat_messages.append({
            'sender': 'bot',
            'message': greeting,
            'emotion': 'neutral',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    current_year = datetime.now().year
    # Pass the show_modal flag to the template
    return render_template('chat.html', chat_history=chat_messages, current_year=current_year, show_modal=show_modal)

@main.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            # Login successful
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            # Set flag to show mood modal on next chat page load
            session['show_mood_modal'] = True 
            return redirect(url_for('main.index'))
        
        flash(error, 'danger')
    
    current_year = datetime.now().year
    return render_template('login.html', current_year=current_year)

@main.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."
        
        if error is None:
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            
            # Auto-login the user after signup
            user = db.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            # Set flag to show mood modal on next chat page load
            session['show_mood_modal'] = True
            
            return redirect(url_for('main.index'))
        
        flash(error, 'danger')
    
    current_year = datetime.now().year
    return render_template('login.html', signup=True, current_year=current_year)

@main.route('/logout')
@login_required
def logout():
    # Clear the mood modal flag on logout
    session.pop('show_mood_modal', None)
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/faq')
def faq():
    current_year = datetime.now().year
    return render_template('faq.html', current_year=current_year)

@main.route('/resources')
def resources():
    current_year = datetime.now().year
    return render_template('resources.html', current_year=current_year)

# Journal Routes
@main.route('/journal')
@login_required
def journal():
    current_year = datetime.now().year
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('journal.html', current_year=current_year, today=today)

@main.route('/journal/entries')
@login_required
def get_journal_entries():
    db = get_db()
    user_id = current_user.id
    
    entries = db.execute(
        '''
        SELECT id, entry_date as date, mood, content, 
               SUBSTR(content, 1, 100) || CASE WHEN LENGTH(content) > 100 THEN "..." ELSE "" END as preview
        FROM journal_entries 
        WHERE user_id = ? 
        ORDER BY entry_date DESC
        ''',
        (user_id,)
    ).fetchall()
    
    # Convert to list of dictionaries
    entries_list = []
    for entry in entries:
        entries_list.append({
            'id': entry['id'],
            'date': entry['date'],
            'mood': entry['mood'],
            'preview': entry['preview']
        })
    
    return jsonify(entries_list)

@main.route('/journal/entry/<date>', methods=['GET', 'POST', 'DELETE'])
@login_required
def journal_entry(date):
    db = get_db()
    user_id = current_user.id
    
    # Validate date format (YYYY-MM-DD)
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if request.method == 'GET':
        # Get an existing entry or return an empty one
        entry = db.execute(
            'SELECT id, entry_date, mood, content FROM journal_entries WHERE user_id = ? AND entry_date = ?',
            (user_id, date)
        ).fetchone()
        
        if entry:
            return jsonify({
                'id': entry['id'],
                'date': entry['entry_date'],
                'mood': entry['mood'],
                'content': entry['content'],
                'is_new': False
            })
        else:
            return jsonify({
                'date': date,
                'mood': None,
                'content': '',
                'is_new': True
            })
    
    elif request.method == 'POST':
        # Create or update an entry
        content = request.json.get('content', '').strip()
        mood = request.json.get('mood')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Check if entry exists
        existing = db.execute(
            'SELECT id FROM journal_entries WHERE user_id = ? AND entry_date = ?',
            (user_id, date)
        ).fetchone()
        
        if existing:
            # Update existing entry
            db.execute(
                'UPDATE journal_entries SET content = ?, mood = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (content, mood, existing['id'])
            )
            message = 'Journal entry updated successfully'
        else:
            # Create new entry
            db.execute(
                'INSERT INTO journal_entries (user_id, entry_date, mood, content) VALUES (?, ?, ?, ?)',
                (user_id, date, mood, content)
            )
            message = 'Journal entry created successfully'
        
        db.commit()
        return jsonify({'message': message, 'success': True})
    
    elif request.method == 'DELETE':
        # Delete an entry
        result = db.execute(
            'DELETE FROM journal_entries WHERE user_id = ? AND entry_date = ?',
            (user_id, date)
        )
        db.commit()
        
        if result.rowcount > 0:
            return jsonify({'message': 'Journal entry deleted successfully', 'success': True})
        else:
            return jsonify({'error': 'Entry not found'}), 404