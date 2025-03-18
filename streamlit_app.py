import streamlit as st
import streamlit.components.v1 as components

st.title("Mappe Interattive con Tooltip")

# Scelta della mappa tramite sidebar
map_option = st.sidebar.selectbox(
    "Seleziona la mappa da visualizzare",
    ("Quartieri", "Unità Urbanistiche", "Municipi")
)

# Determina il file HTML in base alla scelta
if map_option == "Quartieri":
    html_file = "map_quartieri.html"
elif map_option == "Unità Urbanistiche":
    html_file = "map_unita_urbanistiche.html"
else:
    html_file = "map_municipi.html"

# Carica il contenuto del file HTML e mostralo
with open(html_file, "r", encoding="utf-8") as f:
    map_html = f.read()

components.html(map_html, height=600)


