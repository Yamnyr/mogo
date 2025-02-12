import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from streamlit_card import card
import gzip
import streamlit as st

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si Atlas
db = client["movies_db"]
movies_collection = db["movies"]
genres_collection = db["genres"]
production_companies_collection = db["production_companies"]
movie_collections_collection = db["movie_collections"]

TMDB_API_KEY = "c7cf1f564fa32aed665c2abb44d2ffb9"  # Remplace par ta clé API TMDb

# Récupère les détails d'un film à partir de son ID en utilisant l'API TMDb
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=fr-FR"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# Insère des genres dans la collection "genres"
def insert_genres(genres):
    for genre in genres:
        if not genres_collection.find_one({"id": genre["id"]}):
            genres_collection.insert_one({"id": genre["id"], "name": genre["name"]})

# Insère des compagnies de production
def insert_production_companies(companies):
    for company in companies:
        if not production_companies_collection.find_one({"id": company["id"]}):
            production_companies_collection.insert_one({"id": company["id"], "name": company["name"]})

# Insère une collection de films
def insert_movie_collection(movie_collection):
    if movie_collection and not movie_collections_collection.find_one({"id": movie_collection["id"]}):
        movie_collections_collection.insert_one({"id": movie_collection["id"], "name": movie_collection["name"]})

# Récupère les films TMDb et les stocke dans MongoDB (max `limit`).
import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from streamlit_card import card
import gzip
import streamlit as st  # Ajouter cette ligne pour importer Streamlit

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si Atlas
db = client["movies_db"]
movies_collection = db["movies"]
genres_collection = db["genres"]
production_companies_collection = db["production_companies"]
movie_collections_collection = db["movie_collections"]

TMDB_API_KEY = "c7cf1f564fa32aed665c2abb44d2ffb9"  # Remplace par ta clé API TMDb

# Récupère les détails d'un film à partir de son ID en utilisant l'API TMDb
def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=fr-FR"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# [Autres fonctions inchangées...]

# Récupère les films TMDb et les stocke dans MongoDB (max `limit`).
def fetch_and_store_movies(limit=100):
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%m_%d_%Y')
    url = f"https://files.tmdb.org/p/exports/movie_ids_{yesterday}.json.gz"
    
    # Créer une zone pour les logs
    log_container = st.empty()
    progress_bar = st.progress(0)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with gzip.GzipFile(fileobj=response.raw) as file:
            added_movies = 0
            processed_count = 0
            skipped_count = 0
            
            for idx, line in enumerate(file):
                if added_movies >= limit:
                    break

                processed_count += 1
                movie_id = json.loads(line).get("id")
                
                # Mise à jour des logs
                log_container.info(f"🔄 Traitement de la ligne {idx + 1}...")
                
                movie_details = get_movie_details(movie_id)

                if movie_details:
                    if not movies_collection.find_one({"id": movie_details["id"]}):
                        insert_genres(movie_details.get("genres", []))
                        insert_production_companies(movie_details.get("production_companies", []))
                        insert_movie_collection(movie_details.get("belongs_to_collection", {}))

                        movie_details["genres"] = [genre["id"] for genre in movie_details.get("genres", [])]
                        movie_details["production_companies"] = [company["id"] for company in movie_details.get("production_companies", [])]
                        movie_details["belongs_to_collection"] = movie_details["belongs_to_collection"]["id"] if movie_details.get("belongs_to_collection") else None

                        movies_collection.insert_one(movie_details)
                        added_movies += 1
                        log_container.success(f"✅ Film ajouté: {movie_details.get('title', 'Titre inconnu')}")
                    else:
                        skipped_count += 1
                        log_container.warning(f"⚠️ Film déjà existant: ID {movie_id}")
                else:
                    skipped_count += 1
                    log_container.error(f"❌ Impossible de récupérer les détails du film ID {movie_id}")

                progress_bar.progress(min((added_movies / limit), 1.0))

            # Effacer le conteneur de logs temporaire
            log_container.empty()
            
            # Afficher le résumé final
            total_movies = movies_collection.count_documents({})
            st.success(f"""
            ✅ Importation terminée avec succès !
            - {added_movies} nouveaux films ajoutés
            - {skipped_count} films ignorés
            - {processed_count} films traités au total
            
            📊 Nombre total de films dans la base de données : {total_movies}
            """)
            
            return added_movies
            
    except requests.RequestException as e:
        st.error(f"Erreur lors de la récupération des films : {e}")
        return None

def display_movies():
    st.title("🎬 Liste des Films")

    # Initialisation de la page si elle n'existe pas encore dans le session_state
    if 'page' not in st.session_state:
        st.session_state.page = 1  # La page initiale est 1

    # Récupère les films depuis MongoDB
    movies = list(movies_collection.find())  
    if not movies:
        st.warning("Aucun film trouvé dans la base de données.")
        return

    # Pagination
    movies_per_page = 20
    total_pages = (len(movies) - 1) // movies_per_page + 1
    current_page = st.session_state.page  # Utilisation de la page depuis session_state

    # Calculer les indices pour afficher les films de la page actuelle
    start_idx = (current_page - 1) * movies_per_page
    end_idx = start_idx + movies_per_page
    displayed_movies = movies[start_idx:end_idx]

    # Organisation des films en 4 colonnes
    cols = st.columns(4)

    # Affichage des films dans des "cartes"
    for idx, movie in enumerate(displayed_movies):
        with cols[idx % 4]:
            # Construction de l'URL de l'image
            poster_path = movie.get("poster_path")
            if poster_path:
                urlImage = f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                urlImage = "https://via.placeholder.com/500x750?text=Image+non+disponible"
            
            # Affichage de l'image comme carte
            st.markdown(f"""
            <div style=" padding: 10px; border-radius: 10px; width: 300px; height: 700px; margin-bottom: 20px;">
                <img src="{urlImage}" style="width: 100%; height: 450px; border-radius: 8px;">
                <h3>{movie.get('title', 'Titre inconnu')}</h3>
                <p>📅 Sortie : {movie.get('release_date', 'Non dispo')}</p>
                <p>⭐ Note : {movie.get('vote_average', 'N/A')} ({movie.get('vote_count', 0)} votes)</p>
                <p>🌍 Langue : {movie.get('original_language', 'Non dispo')}</p>
            </div>
            """, unsafe_allow_html=True)

    # Affichage des boutons de pagination
    st.write(f"Page {current_page} sur {total_pages}")

    # Colonnes pour la pagination
    col1, col2, col3 = st.columns([1, 3, 1])  # Colonne plus large pour centrer les boutons
    with col1:
        if current_page > 1:
            if st.button("⬅ Précédent"):
                st.session_state.page -= 1
                st.rerun()  # Recharger la page pour afficher la page précédente

    with col3:  # Le bouton "Suivant" dans la colonne de droite
        if current_page < total_pages:
            if st.button("Suivant ➡"):
                st.session_state.page += 1
                st.rerun()  # Recharger la page pour afficher la page suivante