import requests

API_KEY = "VOTRE_API_KEY_TMDB"
BASE_URL = "https://api.themoviedb.org/3"

def search_movie(query):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": query}
    response = requests.get(url, params=params)
    return response.json()

def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": API_KEY}
    response = requests.get(url, params=params)
    return response.json()
