from pymongo import MongoClient
import pandas as pd
import streamlit as st
import plotly.express as px

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["movies_db"]
movies_collection = db["movies"]
genres_collection = db["genres"]
companies_collection = db["production_companies"]
collections_collection = db["movie_collections"]

# --- Fonctions améliorées ---

def get_movie_count():
    """Retourne le nombre total de films en base."""
    return movies_collection.count_documents({})

def get_movies_for_genre(genre_name, limit=5):
    """Retourne une liste des films associés au genre spécifié, triée par popularité."""
    pipeline = [
        {"$unwind": "$genres"},  # Décomposer les genres
        {"$lookup": {
            "from": "genres",
            "localField": "genres", 
            "foreignField": "id",
            "as": "genre_info"
        }},
        {"$unwind": "$genre_info"},  # Décomposer les informations du genre
        {"$match": {"genre_info.name": genre_name}},  # Filtrer par genre
        {"$project": {"_id": 0, "title": 1, "vote_average": 1, "release_date": 1, "popularity": 1}},  # Projeter les champs nécessaires
        {"$sort": {"popularity": -1}},  # Trier par popularité (ordre décroissant)
        {"$limit": limit}  # Limiter aux N films
    ]
    
    return list(movies_collection.aggregate(pipeline))
def get_top_genres():
    """Retourne tous les genres les plus fréquents en tant que dictionnaire pour le graphique."""
    pipeline = [
        {"$unwind": "$genres"},  # Décomposer les genres en documents individuels
        {"$lookup": {
            "from": "genres",  # Jointure avec la collection genres
            "localField": "genres",  # Champ local dans movies
            "foreignField": "id",  # Champ à rejoindre dans genres
            "as": "genre_info"  # Résultat de la jointure sera placé ici
        }},
        {"$unwind": "$genre_info"},  # Décomposer les informations du genre dans genre_info
        {"$group": {
            "_id": "$genre_info.name",  # Group par nom de genre
            "count": { "$sum": 1 }  # Compte le nombre de films par genre
        }},
        {"$sort": { "count": -1 }}  # Trie par ordre décroissant du nombre de films
    ]
    
    return list(movies_collection.aggregate(pipeline))

def get_average_rating():
    """Retourne la note moyenne des films."""
    result = movies_collection.aggregate([
        {"$group": {"_id": None, "avg_rating": {"$avg": "$vote_average"}}}
    ])
    return next(result, {}).get("avg_rating", 0)

def get_movies_per_year():
    """Retourne le nombre de films sortis par année et l'année la plus productive avec ses films."""
    # Calculer le nombre de films par année
    pipeline_count_years = [
        {"$addFields": {
            "year": {"$substr": ["$release_date", 0, 4]}  # Extraire les 4 premiers caractères de la date
        }},
        {"$group": {
            "_id": "$year",  # Groupement par année
            "count": {"$sum": 1}  # Compter le nombre de films par année
        }},
        {"$sort": {"count": -1}}  # Trier par nombre de films décroissant
    ]
    
    # Obtenir le nombre de films par année
    movies_per_year = list(movies_collection.aggregate(pipeline_count_years))
    
    # Si une année est trouvée, extraire les films de cette année
    if movies_per_year:
        top_year = movies_per_year[0]["_id"]
        movies_for_top_year = get_movies_for_year(top_year)  # Appel à la fonction pour récupérer les films pour cette année
        return movies_per_year, movies_for_top_year
    return [], []
def get_movies_for_year(year, limit=10):
    """Retourne les films sortis durant une année spécifiée, triés par popularité."""
    pipeline = [
        {"$addFields": {
            "year": {"$substr": ["$release_date", 0, 4]}  # Extraire l'année à partir de la chaîne de date
        }},
        {"$match": {"year": str(year)}},  # Filtrer par année
        {"$project": {"_id": 0, "title": 1, "vote_average": 1, "release_date": 1, "popularity": 1}},  # Projeter les champs nécessaires
        {"$sort": {"popularity": -1}},  # Trier par popularité (ordre décroissant)
        {"$limit": limit}  # Limiter aux N films
    ]
    return list(movies_collection.aggregate(pipeline))

def get_movies_per_country():
    """Retourne le nombre de films sortis par pays."""
    pipeline = [
        {"$unwind": "$production_countries"},  # Décomposer les pays de production
        {"$group": {
            "_id": "$production_countries.name",  # Regrouper par nom de pays
            "count": {"$sum": 1}  # Compter le nombre de films pour chaque pays
        }},
        {"$sort": {"count": -1}},  # Trier par nombre de films décroissant
        {"$limit": 10}  # Limiter aux 10 pays avec le plus grand nombre de films
    ]
    return list(movies_collection.aggregate(pipeline))

def get_movies_for_country_and_popularity():
    """Retourne les films les plus populaires d'un pays spécifié sans doublons."""
    pipeline = [
        {"$match": {"original_language": "fr"}},  # Filtrer par pays
        {"$group": {
            "_id": "$title",  # Regrouper par titre de film pour éviter les doublons
            "title": {"$first": "$title"},  # Garder le titre du film
            "popularity": {"$first": "$popularity"},  # Garder la popularité du film
            "release_date": {"$first": "$release_date"}  # Garder la date de sortie
        }},
        {"$sort": {"popularity": -1}},  # Trier par popularité (ordre décroissant)
    ]
    return list(movies_collection.aggregate(pipeline))

def get_most_popular_movies(limit=10):
    """Retourne les films les plus populaires."""
    return list(movies_collection.find({}, {"title": 1, "popularity": 1}).sort("popularity", -1).limit(limit))

def plot_statistics():
    """Affiche les statistiques sous forme de graphiques et tables."""
    st.subheader("📊 Statistiques générales")
    st.metric("Nombre total de films", get_movie_count())
    st.metric("Note moyenne des films", round(get_average_rating(), 2))

    # Récupérer tous les genres populaires
    top_genres = get_top_genres()

    if top_genres:
        # Graphique en camembert pour la répartition de tous les genres
        genre_df = pd.DataFrame(top_genres)
        genre_df.columns = ["Genre", "Nombre de films"]
        fig_genres = px.pie(genre_df, names="Genre", values="Nombre de films", title="🎭 Répartition des genres les plus populaires")
        st.plotly_chart(fig_genres)

        # Afficher les films pour les deux genres les plus populaires
        first_genre_name = top_genres[0]["_id"]
        first_genre_movies = get_movies_for_genre(first_genre_name)

        second_genre_name = top_genres[1]["_id"]
        second_genre_movies = get_movies_for_genre(second_genre_name)

        # Afficher les films côte à côte pour les deux genres populaires
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"🎬 Films du genre : {first_genre_name}")
            if first_genre_movies:
                df_first_genre = pd.DataFrame(first_genre_movies)
                st.dataframe(df_first_genre)

        with col2:
            st.subheader(f"🎬 Films du genre : {second_genre_name}")
            if second_genre_movies:
                df_second_genre = pd.DataFrame(second_genre_movies)
                st.dataframe(df_second_genre)

    # Autres graphiques comme les films par année, par pays, etc.
    # Graphique des films par année
    movies_per_year, movies_for_top_year = get_movies_per_year()
    if movies_per_year:
        # Afficher le graphique des films par année
        df_years = pd.DataFrame(movies_per_year)
        df_years.columns = ["Année", "Nombre de films"]
        fig_years = px.bar(df_years, x="Année", y="Nombre de films", title="📅 Nombre de films par année")
        with col1:
            st.plotly_chart(fig_years)

        # Afficher les films de l'année la plus productive
        if movies_for_top_year:
            with col2:
                st.subheader(f"🎬 Films de l'année la plus productive ({movies_per_year[0]['_id']})")
                df_top_year_movies = pd.DataFrame(movies_for_top_year)
                st.dataframe(df_top_year_movies)

    # Graphique des films par pays
    movies_per_country = get_movies_per_country()
    if movies_per_country:
        df_countries = pd.DataFrame(movies_per_country)
        df_countries.columns = ["Pays", "Nombre de films"]
        fig_countries = px.bar(df_countries, x="Pays", y="Nombre de films", title="🌍 Nombre de films par pays")
        with col1: 
            st.plotly_chart(fig_countries)

    # Liste des films français les plus populaires
    french_movies_popular = get_movies_for_country_and_popularity()
    if french_movies_popular:
        # col1, col2 = st.columns(2)

        with col2:
            st.subheader("🎬 Films français les plus populaires")
            df_french_movies = pd.DataFrame(french_movies_popular)
            st.dataframe(df_french_movies)


    # 📌 Graphique des films les plus populaires
    most_popular_movies = get_most_popular_movies()
    if most_popular_movies:
        df_popular = pd.DataFrame(most_popular_movies, columns=["title", "popularity"])
        fig = px.bar(df_popular, x="title", y="popularity", title="🔥 Films les plus populaires", color="popularity")
        st.plotly_chart(fig)    