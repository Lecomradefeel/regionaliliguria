import streamlit as st
import pandas as pd
import folium
import json
from streamlit_folium import st_folium

st.title("Dashboard Interattiva - Visualizzazione Percentuali")

# Selezione del livello geografico tramite sidebar
layer_choice = st.sidebar.selectbox(
    "Seleziona il livello geografico",
    ("Quartieri", "Unità urbanistiche", "Municipi")
)

# Funzioni per caricare i dati (Excel e GeoJSON)
@st.cache_data
def load_excel(file_path):
    return pd.read_excel(file_path)

@st.cache_data
def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# Crea una mappa di base (modifica le coordinate e lo zoom in base alla tua area)
m = folium.Map(location=[44.4268, 8.8882], zoom_start=12)

# Carica e visualizza i dati in base al livello scelto
if layer_choice == "Quartieri":
    st.header("Visualizzazione dei Quartieri")
    # Carica file Excel e GeoJSON per i Quartieri
    df = load_excel("Quartieri con percentuali.xlsx")
    geojson_data = load_geojson("Quartieri.json")
    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=["quartiere", "percentuale"],
        key_on="feature.properties.quartiere",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Percentuale"
    ).add_to(m)

elif layer_choice == "Unità urbanistiche":
    st.header("Visualizzazione delle Unità Urbanistiche")
    # Carica file Excel e GeoJSON per le Unità urbanistiche
    df = load_excel("UU con percentuali.xlsx")
    geojson_data = load_geojson("Unita_urbanistiche (1).json")
    # Assumiamo che la colonna Excel sia "unita" e la proprietà nel GeoJSON "unita"
    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=["unita", "percentuale"],
        key_on="feature.properties.unita",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Percentuale"
    ).add_to(m)

elif layer_choice == "Municipi":
    st.header("Visualizzazione dei Municipi")
    # Carica file Excel e il file TopoJSON/GeoJSON per i Municipi
    df = load_excel("Municipi con percentuali.xlsx")
    geojson_data = load_geojson("Municipi1.json")
    # Assumiamo che la colonna Excel sia "municipio" e che la proprietà nel GeoJSON sia "municipio"
    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=["municipio", "percentuale"],
        key_on="feature.properties.municipio",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Percentuale"
    ).add_to(m)

# Aggiungi il controllo dei layer alla mappa
folium.LayerControl().add_to(m)

st.write("### Mappa Interattiva")
st_folium(m, width=700, height=500)

