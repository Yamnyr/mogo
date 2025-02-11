import streamlit as st
import requests
import gzip
import json
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si Atlas
db = client["movies_db"]
collection = db["movies"]

# Fonction pour récupérer et importer les films depuis TMDb
def fetch_and_store_movies():
    # Date d'hier pour récupérer le bon fichier
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%m_%d_%Y')
    url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday}.json.gz"

    st.write("Récupération des films depuis :", url)

    try:
        # Télécharger le fichier
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Décompresser et lire les données
        with gzip.GzipFile(fileobj=response.raw) as file:
            progress_bar = st.progress(0)
            total_movies = 0
            added_movies = 0

            # Limite du nombre de films à ajouter
            limit = 1000

            # Lecture des lignes
            for idx, line in enumerate(file):
                if added_movies >= limit:
                    break

                movie = json.loads(line)
                
                # Vérifie si le film n'existe pas déjà
                if not collection.find_one({"id": movie["id"]}):
                    collection.insert_one(movie)
                    added_movies += 1

                # Mise à jour de la barre de progression
                progress_bar.progress(min((idx + 1) / limit, 1.0))

            st.success(f"{added_movies} nouveaux films ajoutés à la base de données !")

    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des films : {e}")

# Interface utilisateur Streamlit
st.title("Récupération de films depuis TMDb")

st.write("Cliquez sur le bouton ci-dessous pour récupérer la liste des films d'hier depuis TMDb et les stocker dans MongoDB (max 1000 films).")

if st.button("Récupérer et importer les films"):
    fetch_and_store_movies()
