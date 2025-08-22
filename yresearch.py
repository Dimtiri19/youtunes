import yt_dlp
import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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

# --- Téléchargement audio ---
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '../%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# --- Récupération du genre via Spotify ---
def get_genre_from_file(file_path):
    # Exemple : "Daft Punk - One More Time.mp3"
    base = os.path.basename(file_path)
    if " - " not in base:
        return None
    artist, title_ext = base.split(" - ", 1)
    title = title_ext.rsplit(".", 1)[0]

    # Connexion Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    
    # Recherche du morceau
    results = sp.search(q=f"track:{title} artist:{artist}", type="track", limit=1)
    tracks = results.get("tracks", {}).get("items", [])
    if not tracks:
        return None

    track = tracks[0]
    artist_id = track["artists"][0]["id"]
    artist_info = sp.artist(artist_id)
    return artist_info.get("genres", [])

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Utilisation: python3 youtube_mp3.py \"texte à rechercher\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"🔍 Recherche : {query}")

    lien = search_youtube(query)
    if lien:
        print(f"✅ Vidéo trouvée : {lien}")
        print("⬇️ Téléchargement en MP3...")
        download_audio(lien)
        print("🎵 Téléchargement terminé !")

        # Récupération du fichier téléchargé
        downloaded_file = max([f for f in os.listdir("..") if f.endswith(".mp3")], key=os.path.getctime)
        print(f"🎧 Fichier : {downloaded_file}")

        genres = get_genre_from_file(os.path.join("..", downloaded_file))
        if genres:
            print(f"🎼 Genres Spotify : {', '.join(genres)}")
        else:
            print("❌ Genre non trouvé sur Spotify")
    else:
        print("❌ Aucun résultat trouvé.")
