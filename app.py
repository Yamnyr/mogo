import streamlit as st
from tmdb_utils import display_movies

# Configuration de la page
st.set_page_config(layout="wide")

st.title("🎬 Bienvenue sur l'application TMDb")
st.write("Utilisez cette application pour importer et visualiser des films depuis TMDb.")

# Affichage de la liste des films
display_movies()