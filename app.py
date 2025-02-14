import streamlit as st
from tmdb_utils import display_movies
from movie_details import show_movie_details

# Configuration de la page
st.set_page_config(page_title="Liste des films", page_icon="🎬", layout="wide")

# st.title("🎬 Bienvenue sur l'application TMDb")
# st.write("Utilisez cette application pour importer et visualiser des films depuis TMDb.")

if "selected_movie" in st.session_state and st.session_state.selected_movie:
    show_movie_details()
    st.stop()  # Arrête l'exécution pour ne pas afficher la liste des films

# Affichage de la liste des films
display_movies()