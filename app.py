from stats_utils import plot_statistics
import streamlit as st
from tmdb_utils import fetch_and_store_movies, display_movies
from dashboard_utils import clear_database, add_movie, modify_movie, delete_movie, get_genres, get_production_companies  # Importation de la fonction

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
    number_of_movies = st.selectbox("Sélectionner le nombre de films à importer", [10, 100, 500, 1000], index=2)

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

    # Récupérer la liste des genres depuis la base de données
    genres_list = get_genres()

    # Section pour ajouter un film
    # Formulaire d'ajout de film
    st.subheader("➕ Ajouter un film")
    with st.form("add_movie_form"):
        title = st.text_input("Titre du film")
        release_date = st.date_input("Date de sortie")
        genres = st.multiselect("Genres", genres_list)  # Menu déroulant pour sélectionner plusieurs genres
        overview = st.text_area("Résumé")
        vote_average = st.number_input("Note (0-10)", min_value=0.0, max_value=10.0, step=0.1)
        popularity = st.number_input("Popularité", min_value=0.0, step=0.1)
        budget = st.number_input("Budget", min_value=0)
        revenue = st.number_input("Revenu", min_value=0)
        runtime = st.number_input("Durée (minutes)", min_value=0)
        
        # Récupération des compagnies de production pour le menu déroulant
        production_companies_list = get_production_companies()
        production_companies = st.multiselect(
            "Compagnies de production", 
            [company["name"] for company in production_companies_list]
        )
        
        # spoken_languages = st.text_input("Langues parlées")
        spoken_languages = st.multiselect("Langues parlées", ["English", "French", "Spanish", "German", "Hindi"])

        poster_path = st.text_input("Chemin de l'affiche (URL)")
        imdb_id = st.text_input("ID IMDb")
        tmdb_id = st.text_input("ID TMDb (facultatif)")

        submit_button = st.form_submit_button("Ajouter")

        if submit_button:
            # Filtrage des compagnies de production sélectionnées
            selected_companies = [
                company["id"] for company in production_companies_list if company["name"] in production_companies
            ]
            
            result = add_movie(
                title, 
                str(release_date), 
                genres, 
                overview, 
                vote_average, 
                popularity, 
                budget, 
                revenue, 
                runtime, 
                selected_companies, 
                spoken_languages, 
                poster_path, 
                imdb_id, 
                tmdb_id
            )
            st.success(result)



        # Section pour modifier un film
        st.subheader("✏️ Modifier un film")
        movie_id_to_modify = st.text_input("ID du film à modifier")
        if movie_id_to_modify:
            movie_id_to_modify = movie_id_to_modify.strip()
            movie_id_to_modify = movie_id_to_modify if movie_id_to_modify.isdigit() else None
        
        if movie_id_to_modify:
            with st.form("modify_movie_form"):
                title = st.text_input("Nouveau titre du film")
                release_date = st.date_input("Nouvelle date de sortie")
                genres = st.multiselect("Nouveaux genres", genres_list)  # Menu déroulant pour modifier les genres
                vote_average = st.number_input("Nouvelle note (0-10)", min_value=0.0, max_value=10.0, step=0.1)
                popularity = st.number_input("Nouvelle popularité", min_value=0.0, step=0.1)
                submit_button_modify = st.form_submit_button("Modifier")
                
                if submit_button_modify:
                    result = modify_movie(
                        movie_id_to_modify, title, str(release_date), genres, vote_average, popularity
                    )
                    st.success(result)

    # Section pour supprimer un film
    # Section pour supprimer un film
    st.subheader("🗑 Supprimer un film")
    movie_id_to_delete = st.text_input("ID du film à supprimer")

    # Vérification si l'ID est un entier valide
    if movie_id_to_delete:
        movie_id_to_delete = movie_id_to_delete.strip()
        try:
            # Vérifie si l'ID peut être converti en un entier
            movie_id_to_delete = int(movie_id_to_delete)
        except ValueError:
            movie_id_to_delete = None  # Si ce n'est pas un entier, on le met à None

    if movie_id_to_delete is not None:
        if st.button("Supprimer le film"):
            result = delete_movie(movie_id_to_delete)
            st.success(result)
    else:
        if movie_id_to_delete:
            st.error("❌ L'ID doit être un nombre entier valide.")

elif page == "📈 Statistiques":
    st.title("📈 Statistiques")
    plot_statistics()
