# pages/tmdb_page.py
import streamlit as st
from tmdb_utils import (
    fetch_and_store_movies,
    display_movies,
    movies_collection,
    genres_collection
)

def show_tmdb_page():
    st.title("🎬 TMDb Movies")
    
    # Navigation tabs within the TMDb page

    st.title("📥 Import Movies from TMDb")
    st.write("Import movies from TMDb and store them in MongoDB.")

    # Select number of movies to import
    number_of_movies = st.slider(
        "Select number of movies to import",
        min_value=10,
        max_value=1000,
        step=10,
        value=500
    )

    st.write(f"You have chosen to import {number_of_movies} movies.")

    if st.button("🔄 Fetch and Import Movies"):
        with st.spinner("⏳ Importing..."):
            added_movies = fetch_and_store_movies(limit=number_of_movies)
            if isinstance(added_movies, str):
                st.error(f"❌ {added_movies}")
            else:
                st.success(f"✅ {added_movies} new movies added to database!")

if __name__ == "__main__":
    show_tmdb_page()
