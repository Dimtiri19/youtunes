import yt_dlp
import sys

def search_youtube(query):
    """Recherche la première vidéo YouTube pour un texte donné"""
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch1",  # chercher et prendre le 1er résultat
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if "entries" in info and len(info["entries"]) > 0:
            video = info["entries"][0]
            return f"https://www.youtube.com/watch?v={video['id']}"
        return None

def download_audio(url):
    """Télécharge l'audio en MP3 depuis une URL YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',  # nom du fichier = titre vidéo
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',      # format audio
            'preferredquality': '192',    # qualité
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Utilisation: python3 youtube_mp3.py \"texte à rechercher\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])  # concatène les arguments en un seul texte
    print(f"🔍 Recherche : {query}")

    lien = search_youtube(query)
    if lien:
        print(f"✅ Vidéo trouvée : {lien}")
        print("⬇️ Téléchargement en MP3...")
        download_audio(lien)
        print("🎵 Téléchargement terminé !")
    else:
        print("❌ Aucun résultat trouvé.")
