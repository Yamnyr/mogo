import streamlit as st
from stats_utils import plot_statistics

st.set_page_config(layout="wide")
st.title("📈 Statistiques des Films")
st.write("Explorez les statistiques et tendances de notre base de données de films.")

# Affichage des statistiques
plot_statistics()