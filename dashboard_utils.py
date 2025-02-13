from pymongo import MongoClient
import uuid

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["movies_db"]
movies_collection = db["movies"]
genres_collection = db["genres"]  # Collection des genres
production_companies_collection = db["production_companies"]  # Collection des genres

def clear_database():
    """Supprime tous les films de la base de données."""
    movies_collection.delete_many({})
    return "✅ La base de données a été vidée avec succès !"

def get_genres():
    """Récupère la liste des genres dans la base de données."""
    genres_cursor = genres_collection.find({}, {"_id": 0, "name": 1})
    genres_list = [genre["name"] for genre in genres_cursor]
    return genres_list

def get_genre_name_by_id(genre_id):
    """Récupère le nom d'un genre par son ID."""
    genre = genres_collection.find_one({"id": genre_id}, {"name": 1})
    return genre["name"] if genre else None

def get_production_companies():
    """Récupère la liste des compagnies de production dans la base de données."""
    production_companies_cursor = production_companies_collection.find({}, {"_id": 0, "name": 1, "id": 1})
    production_companies_list = [
        {"name": company["name"], "id": company["id"]} for company in production_companies_cursor
    ]
    return production_companies_list

def add_movie(title, release_date, genres, overview, vote_average, popularity, 
              budget, revenue, runtime, production_companies, spoken_languages, poster_path, imdb_id, tmdb_id):
    """Ajoute un film à la base de données avec un ID égal à tmdb_id."""
    
    movie = {
        "id": tmdb_id,  # Correction : Utiliser tmdb_id comme identifiant unique
        "title": title,
        "release_date": release_date,
        "genres": genres,
        "overview": overview,
        "vote_average": vote_average,
        "popularity": popularity,
        "budget": budget,
        "revenue": revenue,
        "runtime": runtime,
        "spoken_languages": spoken_languages,
        "poster_path": poster_path,
        "imdb_id": imdb_id,
        "production_companies": production_companies,
        "status": "Released",  # Valeur par défaut
        "adult": False,  # Valeur par défaut
    }

    try:
        result = movies_collection.insert_one(movie)
        return f"✅ Film '{title}' ajouté avec succès, ID TMDb : {tmdb_id}"
    except Exception as e:
        return f"❌ Erreur lors de l'ajout du film : {str(e)}"
    
def delete_movie(movie_id):
    """Supprime un film de la base de données."""
    result = movies_collection.delete_one({"id": movie_id})
    if result.deleted_count:
        return f"✅ Film supprimé avec succès (ID : {movie_id})"
    else:
        return "❌ Aucun film trouvé avec cet ID."
    
def get_movie(movie_id):
    """Récupère les informations d'un film par son ID et enrichit les genres avec leurs noms."""
    movie = movies_collection.find_one({"id": movie_id}, {"_id": 0})
    if movie:
        # Convertir les genres en format nom
        genre_names = []
        for genre in movie.get('genres', []):
            genre_name = get_genre_name_by_id(genre.get('id'))
            if genre_name:
                genre_names.append(genre_name)
        movie['genres'] = genre_names
    return movie

def update_movie(movie_id, title, release_date, genres, overview, vote_average, popularity, 
                 budget, revenue, runtime, production_companies, spoken_languages, poster_path, imdb_id):
    """Met à jour les informations d'un film dans la base de données en ajoutant les genres sous format {id, name} et les langues parlées sous format {english_name}."""
    
    # Convertir les noms de genres en format {id, name}
    genres_data = []
    for genre_name in genres:
        genre = genres_collection.find_one({"name": genre_name}, {"_id": 0, "id": 1, "name": 1})
        if genre:
            genres_data.append(genre)
    
    # Convertir les langues parlées en format {english_name}
    spoken_languages_data = [{"english_name": lang} for lang in spoken_languages]

    update_data = {
        "title": title,
        "release_date": release_date,
        "genres": genres_data,  # Utiliser le format {id, name}
        "overview": overview,
        "vote_average": vote_average,
        "popularity": popularity,
        "budget": budget,
        "revenue": revenue,
        "runtime": runtime,
        "production_companies": production_companies,
        "spoken_languages": spoken_languages_data,  # Utiliser le format {english_name}
        "poster_path": poster_path,
        "imdb_id": imdb_id
    }

    try:
        result = movies_collection.update_one(
            {"id": movie_id},
            {"$set": update_data}
        )
        if result.modified_count:
            return f"✅ Film '{title}' modifié avec succès!"
        else:
            return "❌ Aucun film trouvé avec cet ID ou aucune modification effectuée."
    except Exception as e:
        return f"❌ Erreur lors de la modification du film : {str(e)}"
