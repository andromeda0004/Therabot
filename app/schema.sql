DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS chat_history;
DROP TABLE IF EXISTS journal_entries;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sender TEXT NOT NULL, -- 'user' or 'bot'
  message TEXT NOT NULL,
  emotion TEXT, -- emotion detected/used
  FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE journal_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  entry_date TEXT NOT NULL, -- Using TEXT to store ISO date format (YYYY-MM-DD)
  mood TEXT, -- happy, angry, sad, worried, neutral
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id),
  UNIQUE(user_id, entry_date) -- Ensure only one entry per user per date
);

