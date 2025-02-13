import streamlit as st
from datetime import datetime
from dashboard_utils import (
    clear_database, add_movie, delete_movie, get_genres, 
    get_production_companies, get_movie, update_movie
)

st.title("📊 Dashboard")
st.write("🚀 Ici, vous pouvez gérer les films stockés dans la base de données.")

# Bouton pour vider la base de données
if st.button("🗑 Vider la base de données"):
    message = clear_database()
    st.success(message)

# Récupérer la liste des genres depuis la base de données
genres_list = get_genres()

# Section pour ajouter un film
st.subheader("➕ Ajouter un film")
with st.form("add_movie_form"):
    title = st.text_input("Titre du film")
    release_date = st.date_input("Date de sortie")
    genres = st.multiselect("Genres", genres_list)
    overview = st.text_area("Résumé")
    vote_average = st.number_input("Note (0-10)", min_value=0.0, max_value=10.0, step=0.1)
    popularity = st.number_input("Popularité", min_value=0.0, step=0.1)
    budget = st.number_input("Budget", min_value=0)
    revenue = st.number_input("Revenu", min_value=0)
    runtime = st.number_input("Durée (minutes)", min_value=0)
    
    production_companies_list = get_production_companies()
    production_companies = st.multiselect(
        "Compagnies de production", 
        [company["name"] for company in production_companies_list]
    )
    
    spoken_languages = st.multiselect("Langues parlées", ["English", "French", "Spanish", "German", "Hindi"])
    poster_path = st.text_input("Chemin de l'affiche (URL)")
    imdb_id = st.text_input("ID IMDb")
    tmdb_id = st.number_input("ID TMDb", min_value=0, step=1, format="%d")

    submit_button = st.form_submit_button("Ajouter")

    if submit_button:
        if not title or not release_date or not genres or not overview or popularity is None or not production_companies or not tmdb_id:
            st.error("❌ Veuillez remplir tous les champs obligatoires (Titre, Date de sortie, Genres, Résumé, Note, Popularité, ID TMDb).")
        else:
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
movie_id_to_update = st.text_input("ID du film à modifier")

if movie_id_to_update:
    try:
        movie_id_to_update = int(movie_id_to_update.strip())
        movie = get_movie(movie_id_to_update)  # Cette fonction retourne maintenant les noms des genres
        
        if movie:
            st.success(f"Film trouvé : {movie['title']}")
            
            with st.form(key="update_movie_form"):
                title = st.text_input("Titre du film", value=movie.get('title', ''))
                
                # Conversion de la date de string à datetime
                try:
                    current_date = datetime.strptime(movie.get('release_date', ''), '%Y-%m-%d').date()
                except ValueError:
                    current_date = datetime.now().date()
                
                release_date = st.date_input("Date de sortie", value=current_date)
                
                # Les genres sont maintenant déjà au format nom
                genres = st.multiselect("Genres", genres_list, default=movie.get('genres', []))
                
                overview = st.text_area("Résumé", value=movie.get('overview', ''))
                vote_average = st.number_input("Note (0-10)", min_value=0.0, max_value=10.0, step=0.1, value=float(movie.get('vote_average', 0)))
                popularity = st.number_input("Popularité", min_value=0.0, step=0.1, value=float(movie.get('popularity', 0)))
                budget = st.number_input("Budget", min_value=0, value=int(movie.get('budget', 0)))
                revenue = st.number_input("Revenu", min_value=0, value=int(movie.get('revenue', 0)))
                runtime = st.number_input("Durée (minutes)", min_value=0, value=int(movie.get('runtime', 0)))
                
                # Gestion des compagnies de production
                current_companies = []
                for company_id in movie.get('production_companies', []):
                    for company in production_companies_list:
                        if company['id'] == company_id:
                            current_companies.append(company['name'])
                            break
                
                available_companies = [company["name"] for company in production_companies_list]
                default_companies = [company for company in current_companies if company in available_companies]
                
                production_companies = st.multiselect(
                    "Compagnies de production",
                    available_companies,
                    default=default_companies
                )

                # Gestion des langues parlées
                available_languages = ["English", "French", "Spanish", "German", "Hindi"]
                current_languages = [lang["english_name"] for lang in movie.get('spoken_languages', [])]
                default_languages = [lang for lang in current_languages if lang in available_languages]
                
                spoken_languages = st.multiselect(
                    "Langues parlées",
                    available_languages,
                    default=default_languages
                )
                
                poster_path = st.text_input("Chemin de l'affiche (URL)", value=movie.get('poster_path', ''))
                imdb_id = st.text_input("ID IMDb", value=movie.get('imdb_id', ''))

                # Bouton de soumission du formulaire
                submit_button = st.form_submit_button("Mettre à jour le film")

                if submit_button:
                    if not title or not release_date or not genres or not overview or popularity is None:
                        st.error("❌ Veuillez remplir tous les champs obligatoires.")
                    else:
                        selected_companies = [
                            company["id"] for company in production_companies_list 
                            if company["name"] in production_companies
                        ]

                        result = update_movie(
                            movie_id_to_update,
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
                            imdb_id
                        )
                        st.success(result)
        else:
            st.error("❌ Aucun film trouvé avec cet ID.")
            
    except ValueError:
        st.error("❌ L'ID doit être un nombre entier valide.")

# Section pour supprimer un film
st.subheader("🗑 Supprimer un film")
movie_id_to_delete = st.text_input("ID du film à supprimer")

if movie_id_to_delete:
    movie_id_to_delete = movie_id_to_delete.strip()
    try:
        movie_id_to_delete = int(movie_id_to_delete)
    except ValueError:
        movie_id_to_delete = None

if movie_id_to_delete is not None:
    if st.button("Supprimer le film"):
        result = delete_movie(movie_id_to_delete)
        st.success(result)
else:
    if movie_id_to_delete:
        st.error("❌ L'ID doit être un nombre entier valide.")