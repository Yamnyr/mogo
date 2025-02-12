from pymongo import MongoClient
import pandas as pd
import streamlit as st
import plotly.express as px

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["movies_db"]
movies_collection = db["movies"]

def get_movie_count():
    """Retourne le nombre total de films en base."""
    return movies_collection.count_documents({})

def get_top_genres():
    """Retourne les genres les plus fréquents."""
    pipeline = [
        {"$unwind": "$genres"},
        {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    return list(movies_collection.aggregate(pipeline))

def get_average_rating():
    """Retourne la note moyenne des films."""
    result = movies_collection.aggregate([
        {"$group": {"_id": None, "avg_rating": {"$avg": "$vote_average"}}}
    ])
    return next(result, {}).get("avg_rating", 0)

def get_movies_per_year():
    """Retourne le nombre de films sortis par année."""
    pipeline = [
        {"$group": {"_id": {"$substr": ["$release_date", 0, 4]}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    return list(movies_collection.aggregate(pipeline))

def plot_statistics():
    """Affiche les statistiques sous forme de graphiques."""
    st.subheader("📊 Statistiques générales")
    st.metric("Nombre total de films", get_movie_count())
    st.metric("Note moyenne des films", round(get_average_rating(), 2))
    
    # Graphique des genres les plus populaires
    genres = get_top_genres()
    if genres:
        df_genres = pd.DataFrame(genres)
        df_genres.columns = ["Genre", "Nombre de films"]
        fig = px.bar(df_genres, x="Genre", y="Nombre de films", title="🎭 Top 10 des genres de films")
        st.plotly_chart(fig)
    
    # Graphique des films par année
    movies_per_year = get_movies_per_year()
    if movies_per_year:
        df_years = pd.DataFrame(movies_per_year)
        df_years.columns = ["Année", "Nombre de films"]
        fig = px.line(df_years, x="Année", y="Nombre de films", title="📅 Nombre de films par année")
        st.plotly_chart(fig)
