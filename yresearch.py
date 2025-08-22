import yt_dlp 
import sys
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

last_file = None  # variable globale pour stocker le fichier final

# --- Hook pour savoir quand le fichier est fini ---
def my_hook(d):
    global last_file
    if d['status'] == 'finished':
        last_file = d['filename']
        print(f"✅ Téléchargement terminé : {last_file}")

# --- Nettoyage du titre pour Spotify ---
def clean_title(title):
    # Supprime tout ce qui est entre parenthèses ou crochets
    title = re.sub(r"[\(\[].*?[\)\]]", "", title)
    # Supprime 'feat.', 'ft.' ou 'featuring' suivi d’un nom
    title = re.sub(r"\s+(feat\.|ft\.|featuring)\s+.*", "", title, flags=re.IGNORECASE)
    # Supprime espaces au début et à la fin
    return title.strip()

# --- Recherche YouTube ---
def search_youtube(query):
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch1",
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info and len(info["entries"]) > 0:
            video = info["entries"][0]
            return f"https://www.youtube.com/watch?v={video['id']}"
        return None

# --- Téléchargement audio (format WebM/Opus) ---
def download_audio(url):
    global last_file
    ydl_opts = {
        'format': 'bestaudio[ext=webm]',
        'outtmpl': '../%(title)s.%(ext)s',  # garde l'extension originale (.webm)
        'progress_hooks': [my_hook],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return last_file

# --- Récupération des infos Spotify (genres + album + date) ---
def get_track_info_from_file(file_path):
    base = os.path.basename(file_path)
    if " - " not in base:
        return {"error": "Format fichier invalide"}
    
    artist, title_ext = base.split(" - ", 1)
    title = title_ext.rsplit(".", 1)[0]
    title = clean_title(title)

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    
    # Recherche du morceau
    results = sp.search(q=f"track:{title} artist:{artist}", type="track", limit=3)
    tracks = results.get("tracks", {}).get("items", [])

    if not tracks:
        # Vérifie si l'artiste existe au moins
        artist_results = sp.search(q=f"artist:{artist}", type="artist", limit=1)
        if not artist_results.get("artists", {}).get("items", []):
            return {"error": "Auteur non trouvé"}
        else:
            return {"error": "Titre trouvé mais pas d’artiste correspondant"}

    track = tracks[0]
    artist_id = track["artists"][0]["id"]
    artist_info = sp.artist(artist_id)
    genres = artist_info.get("genres", [])

    album_name = track["album"]["name"]
    release_date = track["album"]["release_date"]

    return {
        "genres": genres if genres else ["Genre non trouvé"],
        "album": album_name,
        "release_date": release_date
    }

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Utilisation: python3 youtube_audio.py \"texte à rechercher\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Recherche : {query}")

    lien = search_youtube(query)
    if lien:
        print(f"✅ Vidéo trouvée : {lien}")
        print("⬇️ Téléchargement de l’audio...")
        downloaded_file = download_audio(lien)
        print(f"🎧 Fichier téléchargé : {downloaded_file}")

        info = get_track_info_from_file(downloaded_file)
        if "error" in info:
            print(f"⚠️ {info['error']}")
        else:
            print(f"🎼 Genres Spotify : {', '.join(info['genres'])}")
            print(f"💿 Album : {info['album']}")
            print(f"📅 Date de sortie : {info['release_date']}")
    else:
        print("❌ Aucun résultat trouvé.")