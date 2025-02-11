import requests
import gzip
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import streamlit as st

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si Atlas
db = client["movies_db"]
collection = db["movies"]

def fetch_and_store_movies(limit=1000):
    """
    Récupère les films TMDb et les stocke dans MongoDB (max `limit`).
    """
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%m_%d_%Y')
    url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday}.json.gz"
    st.write(f"Récupération des films depuis : {url}")

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
                movie = json.loads(line)
                
                # Vérifie si le film n'existe pas déjà
                if not collection.find_one({"id": movie["id"]}):
                    collection.insert_one(movie)
                    added_movies += 1

                # Mise à jour de la barre de progression
                progress_bar.progress(min((added_movies / limit), 1.0))

            return added_movies
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des films : {e}")
        return None
