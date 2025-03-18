import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import json
from branca.colormap import linear

# Configurazione della pagina
st.set_page_config(layout="wide", page_title="Dashboard Mappe Interattive")

# Titolo principale
st.title("Dashboard Mappe Interattive con Tooltip")

# Sidebar per selezione
with st.sidebar:
    st.header("Configurazione")
    map_option = st.selectbox(
        "Seleziona la mappa da visualizzare",
        ("Quartieri", "Unità Urbanistiche", "Municipi")
    )
    
    # Opzioni aggiuntive
    show_labels = st.checkbox("Mostra etichette", value=True)
    map_style = st.selectbox(
        "Stile mappa",
        ("OpenStreetMap", "Stamen Terrain", "Stamen Toner", "CartoDB positron")
    )

# Funzione per creare mappe con Folium
def create_map(geo_data, data_field="name", tooltip_fields=None, title=""):
    # Determina il centro della mappa (media delle coordinate)
    if geo_data is not None:
        center = [geo_data.geometry.centroid.y.mean(), geo_data.geometry.centroid.x.mean()]
    else:
        # Default a Bologna, Italia
        center = [44.4949, 11.3426]
    
    # Crea la mappa base
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles=map_style
    )
    
    if geo_data is not None:
        # Converti GeoDataFrame in GeoJSON
        geo_json_data = json.loads(geo_data.to_json())
        
        # Crea una scala di colori basata sui valori
        if "value" in geo_data.columns:
            colormap = linear.YlOrRd_09.scale(
                geo_data["value"].min(),
                geo_data["value"].max()
            )
            
            # Aggiungi la legenda
            colormap.caption = "Valore"
            m.add_child(colormap)
        
        # Aggiungi il layer GeoJSON
        folium.GeoJson(
            geo_json_data,
            name=title,
            style_function=lambda feature: {
                'fillColor': colormap(feature['properties']['value']) if 'value' in feature['properties'] else '#3388ff',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            },
            tooltip=folium.GeoJsonTooltip(
                fields=tooltip_fields if tooltip_fields else [data_field],
                aliases=tooltip_fields if tooltip_fields else [data_field],
                localize=True,
                sticky=False,
                labels=True
            )
        ).add_to(m)
        
        # Aggiungi etichette se richiesto
        if show_labels:
            for idx, row in geo_data.iterrows():
                # Prendi il centroide della geometria
                centroid = row.geometry.centroid
                # Aggiungi un marker con etichetta
                folium.Marker(
                    [centroid.y, centroid.x],
                    icon=folium.DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(75, 18),
                        html=f'<div style="font-size: 10pt; color: black; text-align: center;">{row[data_field]}</div>'
                    )
                ).add_to(m)
    
    return m

# Carica i dati di esempio
# Nota: In un'applicazione reale, questi dati sarebbero caricati da file o API
@st.cache_data
def load_example_data(option):
    """
    Carica dati di esempio per le diverse opzioni.
    In un'applicazione reale, caricheresti i tuoi dati reali.
    """
    # Crea un GeoDataFrame di esempio
    if option == "Quartieri":
        # Esempio di quartieri di Bologna
        data = {
            'name': ['Borgo Panigale-Reno', 'Navile', 'Porto-Saragozza', 'San Donato-San Vitale', 'Santo Stefano', 'Savena'],
            'value': [150, 230, 310, 180, 280, 200],
            'population': [60000, 68000, 65000, 63000, 58000, 59000],
            'geometry': None  # Qui andresti a inserire le geometrie reali
        }
    elif option == "Unità Urbanistiche":
        # Esempio di unità urbanistiche
        data = {
            'name': ['Barca', 'Mazzini', 'Bolognina', 'Corticella', 'Saffi', 'Marconi', 'San Donato', 'Colli'],
            'value': [120, 150, 200, 180, 160, 210, 170, 190],
            'population': [15000, 18000, 22000, 16000, 19000, 20000, 17000, 14000],
            'geometry': None  # Qui andresti a inserire le geometrie reali
        }
    else:  # Municipi
        data = {
            'name': ['Municipio I', 'Municipio II', 'Municipio III', 'Municipio IV', 'Municipio V', 'Municipio VI'],
            'value': [350, 420, 380, 400, 450, 370],
            'population': [80000, 95000, 85000, 90000, 100000, 78000],
            'geometry': None  # Qui andresti a inserire le geometrie reali
        }
    
    # Crea un GeoDataFrame fittizio
    from shapely.geometry import Polygon
    import numpy as np
    
    # Crea alcune geometrie di esempio
    n = len(data['name'])
    geometries = []
    center_x, center_y = 11.3426, 44.4949  # Bologna, Italia
    
    for i in range(n):
        # Crea un poligono irregolare attorno al centro
        angle = (i / n) * 2 * np.pi
        radius = 0.03 + 0.01 * np.sin(i * 3.14)
        points = []
        for j in range(6):  # Esagono irregolare
            a = angle + (j / 6) * 2 * np.pi
            r = radius * (0.8 + 0.4 * np.random.random())
            x = center_x + r * np.cos(a)
            y = center_y + r * np.sin(a)
            points.append((x, y))
        points.append(points[0])  # Chiudi il poligono
        geometries.append(Polygon(points))
    
    data['geometry'] = geometries
    gdf = gpd.GeoDataFrame(data, geometry='geometry', crs="EPSG:4326")
    return gdf

# Carica i dati in base alla selezione
geo_data = load_example_data(map_option)

# Crea la mappa
tooltip_fields = ['name', 'value', 'population']
m = create_map(geo_data, data_field="name", tooltip_fields=tooltip_fields, title=map_option)

# Layout della dashboard
col1, col2 = st.columns([3, 1])

with col1:
    # Mostra la mappa
    st.subheader(f"Mappa {map_option}")
    folium_static(m, width=800, height=600)

with col2:
    # Mostra statistiche e informazioni
    st.subheader("Statistiche")
    
    # Mostra una tabella con i dati
    st.dataframe(geo_data[['name', 'value', 'population']])
    
    # Aggiungi alcuni grafici
    st.subheader("Grafico valori")
    st.bar_chart(geo_data.set_index('name')['value'])
    
    st.subheader("Distribuzione popolazione")
    st.bar_chart(geo_data.set_index('name')['population'])

# Aggiungi note e istruzioni
st.markdown("---")
st.markdown("""
### Note:
- I dati mostrati sono di esempio. In un'applicazione reale, sostituirli con dati geografici reali.
- Per caricare dati geografici reali, usa file GeoJSON o Shapefile.
- Questa dashboard è ottimizzata per funzionare su Streamlit Cloud.
""")

# Mostra informazioni sull'ambiente
st.sidebar.markdown("---")
st.sidebar.info("""
### Requisiti:
- streamlit
- folium
- streamlit-folium
- pandas
- geopandas
- shapely
""")
