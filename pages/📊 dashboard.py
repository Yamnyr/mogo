import streamlit as st
from dashboard_utils import clear_database, add_movie, delete_movie, get_genres, get_production_companies

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