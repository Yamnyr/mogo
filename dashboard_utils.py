from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si nécessaire
db = client["movies_db"]
movies_collection = db["movies"]

def clear_database():
    """Supprime tous les films de la base de données."""
    movies_collection.delete_many({})
    return "✅ La base de données a été vidée avec succès !"
