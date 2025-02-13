import streamlit as st
from tmdb_utils import display_movies

# Configuration de la page
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebarNav"] ul li a[href$="movie_details"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎬 Bienvenue sur l'application TMDb")
st.write("Utilisez cette application pour importer et visualiser des films depuis TMDb.")

# Affichage de la liste des films
display_movies()