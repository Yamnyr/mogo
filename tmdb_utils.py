import requests
import time
import pandas as pd
import json
import gzip
from datetime import datetime, timedelta

API_KEY = 'c7cf1f564fa32aed665c2abb44d2ffb9'
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'


def get_movie_details(movie_id):
    """Obtenir les détails d'un film donné via son ID"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {'api_key': API_KEY, 'language': 'fr-FR'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            'id': movie_id,
            'title': data.get('title'),
            'release_date': data.get('release_date'),
            'genres': [genre['name'] for genre in data.get('genres', [])],
            'popularity': data.get('popularity'),
            'vote_average': data.get('vote_average'),
            'poster_url': f"{IMAGE_BASE_URL}{data.get('poster_path')}" if data.get('poster_path') else None,
            'overview': data.get('overview', 'Pas de synopsis disponible')
        }
    return None
