import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import gzip
import streamlit as st  # Ajouter cette ligne pour importer Streamlit

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si Atlas
db = client["movies_db"]
collection = db["movies"]

TMDB_API_KEY = "c7cf1f564fa32aed665c2abb44d2ffb9"  # Remplace par ta clé API TMDb
# recupère les détails d'un film a partir de son id tmdb via une reuete ai tmdb
def get_movie_details(movie_id):
    """
    Récupère les détails d'un film à partir de son ID en utilisant l'API TMDb.
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=fr-FR"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Retourne les détails du film en JSON
    else:
        return None

# recupère le ficheir contenant la liste de touss les films mis a jour hier 
def fetch_and_store_movies(limit=1000):
    """
    Récupère les films TMDb et les stocke dans MongoDB (max `limit`).
    """
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%m_%d_%Y')
    url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday}.json.gz"
    
    try:
        # Télécharger le fichier
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Décompresser et lire les données
        with gzip.GzipFile(fileobj=response.raw) as file:
            total_movies = 0
            added_movies = 0
            progress_bar = st.progress(0)  # Créer la barre de progression

            # Lecture de chaque ligne du fichier
            for idx, line in enumerate(file):
                if added_movies >= limit:
                    break

                # On récupère uniquement l'ID du film depuis le fichier
                movie_id = json.loads(line).get("id")
                
                # Récupérer les détails du film via l'API TMDb
                movie_details = get_movie_details(movie_id)
                
                if movie_details:
                    # Vérifie si le film n'existe pas déjà dans MongoDB
                    if not collection.find_one({"id": movie_details["id"]}):
                        collection.insert_one(movie_details)  # Ajouter à MongoDB
                        added_movies += 1

                # Mise à jour de la barre de progression
                progress_bar.progress(min((added_movies / limit), 1.0))

            return added_movies
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des films : {e}")
        return None

def display_movies(limit=10):
    st.title("🎬 Liste des Films")

    movies = list(collection.find().limit(limit))

    if not movies:
        st.warning("Aucun film trouvé dans la base de données.")
        return

    # Organisation des films en 4 colonnes avec espace entre elles
    cols = st.columns(4, gap="large")  # Ajoute un espace entre les colonnes

    for idx, movie in enumerate(movies):
        with cols[idx % 4]:  # Répartit les films dans les 4 colonnes
            with st.container():
                st.image(f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}", 
                         caption=movie.get("title", "Titre inconnu"))
                st.subheader(movie.get("title", "Titre inconnu"))
                st.write(f"📅 **Sortie :** {movie.get('release_date', 'Non dispo')}")
                st.write(f"⭐ **Note :** {movie.get('vote_average', 'N/A')} ({movie.get('vote_count', 0)} votes)")
                st.write(f"🌍 **Langue :** {movie.get('original_language', 'Non dispo')}")
                st.write(f"📝 **Résumé :** {movie.get('overview', 'Pas de résumé')}")