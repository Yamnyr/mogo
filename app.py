import streamlit as st
from pymongo import MongoClient
import tmdb_utils

# Connexion MongoDB
client = MongoClient("VOTRE_URI_MONGODB")
db = client["movies_db"]
collection = db["favorites"]

st.title("Recherche de Films avec TMDb")

# Recherche de films
query = st.text_input("Entrez le nom d'un film :")
if query:
    results = tmdb_utils.search_movie(query)
    if results["results"]:
        for movie in results["results"]:
            st.subheader(movie["title"])
            st.write("Résumé :", movie.get("overview", "Pas de description disponible"))

            # Sauvegarder en BDD
            if st.button(f"Ajouter '{movie['title']}' aux favoris", key=movie["id"]):
                collection.insert_one(movie)
                st.success(f"'{movie['title']}' ajouté aux favoris !")

# Afficher les films favoris
st.subheader("Mes films favoris")
favorites = collection.find()
for movie in favorites:
    st.write(f"- {movie['title']}")
