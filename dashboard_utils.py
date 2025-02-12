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

def get_production_companies():
    """Récupère la liste des compagnies de production dans la base de données."""
    production_companies_cursor = production_companies_collection.find({}, {"_id": 0, "name": 1, "id": 1})
    production_companies_list = [
        {"name": company["name"], "id": company["id"]} for company in production_companies_cursor
    ]
    return production_companies_list

def add_movie(title, release_date, genres, overview, vote_average, popularity, 
              budget, revenue, runtime, production_countries, spoken_languages, poster_path, imdb_id, tagline, tmdb_id=None):
    """Ajoute un film à la base de données."""
    # Vérification de l'ID TMDb ou générer un ID unique si nécessaire
    movie_id = tmdb_id if tmdb_id else str(uuid.uuid4())  # Utilise un UUID si TMDb ID est vide
    
    movie = {
        "id": movie_id,  # Utilisation d'un ID unique généré ou fourni
        "title": title,
        "release_date": release_date,
        "genres": genres,  # Liste de genres
        "overview": overview,
        "vote_average": vote_average,
        "popularity": popularity,
        "budget": budget,
        "revenue": revenue,
        "runtime": runtime,
        "production_countries": production_countries,
        "spoken_languages": spoken_languages,
        "poster_path": poster_path,
        "imdb_id": imdb_id,
        # "tagline": tagline,
        "status": "Released",  # Par défaut, on peut définir un statut de "Released"
        "adult": False,  # Par défaut, on peut définir "adult" à False
    }

    try:
        result = movies_collection.insert_one(movie)
        return f"✅ Film '{title}' ajouté avec succès, ID : {result.inserted_id}"
    except Exception as e:
        return f"❌ Erreur lors de l'ajout du film : {str(e)}"

def modify_movie(movie_id, title=None, release_date=None, genres=None, vote_average=None, popularity=None):
    """Modifie un film existant dans la base de données."""
    updated_fields = {}
    
    if title:
        updated_fields["title"] = title
    if release_date:
        updated_fields["release_date"] = release_date
    if genres:
        updated_fields["genres"] = genres
    if vote_average:
        updated_fields["vote_average"] = vote_average
    if popularity:
        updated_fields["popularity"] = popularity
    
    if updated_fields:
        result = movies_collection.update_one({"_id": movie_id}, {"$set": updated_fields})
        if result.matched_count:
            return f"✅ Film modifié avec succès (ID : {movie_id})"
        else:
            return "❌ Aucun film trouvé avec cet ID."
    return "❌ Aucune modification apportée."

def delete_movie(movie_id):
    """Supprime un film de la base de données."""
    result = movies_collection.delete_one({"id": movie_id})
    if result.deleted_count:
        return f"✅ Film supprimé avec succès (ID : {movie_id})"
    else:
        return "❌ Aucun film trouvé avec cet ID."
