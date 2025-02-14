import streamlit as st
from pymongo import MongoClient

def show_movie_details():
    # Connexion à MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["movies_db"]
    movies_collection = db["movies"]
    genres_collection = db["genres"]
    movie_collections = db["movie_collections"]
    production_companies = db["production_companies"]

    st.title("🎬 Détails du Film")
    # ✅ Bouton retour avec suppression de `selected_movie`
        
    # import streamlit as st

    col1, col2 = st.columns([1, 1])  # Colonnes de taille égale

    with col1:
        if st.button("⬅ Retour à la liste", use_container_width=True):  # Ajuste la largeur
            del st.session_state.selected_movie
            st.rerun()

    with col2:
        if st.button("🏴‍☠️", use_container_width=True):  # Ajuste la largeur
            st.session_state.show_player = not st.session_state.show_player
            st.rerun()

    # Vérifier si un film a été sélectionné
    if "selected_movie" not in st.session_state or st.session_state.selected_movie is None:
        st.warning("Aucun film sélectionné. Retour à la liste des films.")
        st.experimental_rerun()

    # Récupérer l'ID du film sélectionné
    movie_id = int(st.session_state.selected_movie)  # Conversion explicite en entier

    # Récupérer le film avec l'ID
    movie = movies_collection.find_one({"id": movie_id})

    # Afficher les détails du film
    if movie:
        tmdb_id = movie.get("id", None)
        st.session_state.show_player = st.session_state.get("show_player", False)

        

        if st.session_state.show_player:
            tmdb_id = movie.get("id", None)
            if tmdb_id:
                iframe_url = f"https://player.vidbinge.com/media/tmdb-movie-{tmdb_id}"
                st.markdown(
                    f'<iframe src="{iframe_url}" width="100%" height="800px" frameborder="0" allowfullscreen></iframe>',
                    unsafe_allow_html=True
            )


        col1, col2 = st.columns([2, 3])
        with col1:
            poster_path = movie.get("poster_path", "")
            if poster_path:
                st.image(f"https://image.tmdb.org/t/p/w500{poster_path}")

        with col2:
            st.subheader(movie.get("title", "Titre inconnu"))
            st.write(f"**Id :** {movie.get('id')}")
            st.write(f"**Date de sortie :** {movie.get('release_date', 'Non disponible')}")
            st.write(f"**Note :** {movie.get('vote_average', 'N/A')} ({movie.get('vote_count', 0)} votes)")

            # Genres
            genre_ids = [genre["id"] for genre in movie.get("genres", [])]
            genre_map = {genre["id"]: genre["name"] for genre in genres_collection.find()}
            genre_names = [genre_map.get(genre_id, "Inconnu") for genre_id in genre_ids]
            st.write(f"**Genres :** {', '.join(genre_names) if genre_names else 'Non disponible'}")

            st.write(f"**Durée :** {movie.get('runtime', 'Non disponible')} minutes")
            st.write(f"**Revenue :** {movie.get('revenue', 0)} USD")
            st.write(f"**Synopsis :** {movie.get('overview', 'Aucun synopsis disponible.')}")

            collection_id = movie.get("belongs_to_collection", None)
            if collection_id:
                collection = movie_collections.find_one({"id": collection_id})
                collection_name = collection.get("name", "Non disponible") if collection else "Non disponible"
                st.write(f"**Collection :** {collection_name}")
            else:
                st.write("**Collection :** Aucune")

            imdb_id = movie.get("imdb_id", "Non disponible")
            st.write(f"**IMDb :** [Lien IMDb](https://www.imdb.com/title/{imdb_id})" if imdb_id != "Non disponible" else "IMDb : Non disponible")

            origin_country = ", ".join(movie.get("origin_country", ["Non disponible"]))
            st.write(f"**Pays d'origine :** {origin_country}")

            spoken_languages = ", ".join([lang.get("name", "Inconnu") for lang in movie.get("spoken_languages", [])])
            st.write(f"**Langues parlées :** {spoken_languages if spoken_languages else 'Non disponible'}")

            production_company_ids = movie.get("production_companies", [])
            production_company_names = []
            for company_id in production_company_ids:
                company = production_companies.find_one({"id": company_id})
                if company:
                    production_company_names.append(company.get("name", "Inconnu"))
            st.write(f"**Compagnies de production :** {', '.join(production_company_names) if production_company_names else 'Non disponible'}")

            production_countries = ", ".join([country.get("name", "Inconnu") for country in movie.get("production_countries", [])])
            st.write(f"**Pays de production :** {production_countries if production_countries else 'Non disponible'}")