from stats_utils import plot_statistics
import streamlit as st
from tmdb_utils import fetch_and_store_movies, display_movies
from dashboard_utils import clear_database  # Importation de la fonction

# Permet de remplir toute la largeur de la page
st.set_page_config(layout="wide")

# Navigation avec icônes
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("📂 Choisir une page", ["🏠 Accueil", "📥 Importer des films", "📊 Dashboard", "📈 Statistiques"])

if page == "🏠 Accueil":
    st.title("🎬 Bienvenue sur l'application TMDb")
    st.write("Utilisez cette application pour importer et visualiser des films depuis TMDb.")
    display_movies()

elif page == "📥 Importer des films":
    st.title("📥 Importation de films depuis TMDb")
    st.write("Cliquez sur le bouton ci-dessous pour récupérer la liste des films d'hier depuis TMDb et les stocker dans MongoDB.")

    # Sélection du nombre de films à importer
    number_of_movies = st.selectbox("Sélectionner le nombre de films à importer", [10, 100, 1000, 10000], index=2)

    st.write(f"Vous avez choisi d'importer {number_of_movies} films.")

    if st.button("🔄 Récupérer et importer les films"):
        with st.spinner("⏳ Importation en cours..."):
            added_movies = fetch_and_store_movies(limit=number_of_movies)
            if isinstance(added_movies, str):  # Gestion des erreurs
                st.error(f"❌ {added_movies}")
            else:
                st.success(f"✅ {added_movies} nouveaux films ajoutés à la base de données !")

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.write("🚀 Ici, vous pouvez gérer les films stockés dans la base de données.")

    # Bouton pour vider la base de données
    if st.button("🗑 Vider la base de données"):
        message = clear_database()  # Appel de la fonction pour vider la BDD
        st.success(message)

elif page == "📈 Statistiques":
    st.title("📈 Statistiques")
    plot_statistics()
