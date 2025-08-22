import sqlite3

conn = sqlite3.connect("music.db")
c = conn.cursor()

# Table musiques
c.execute("""
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    genres TEXT,
    album TEXT,
    release_date TEXT,
    file_path TEXT UNIQUE
)
""")

# Table utilisateurs
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT
)
""")

# Table playlists
c.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# Table relation playlists ↔ musiques
c.execute("""
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INTEGER,
    track_id INTEGER,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
)
""")

conn.commit()
conn.close()
