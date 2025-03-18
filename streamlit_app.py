import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import json
import os
from branca.colormap import linear

# Configurazione della pagina
st.set_page_config(layout="wide", page_title="Dashboard Mappe Interattive")

# Titolo principale
st.title("Dashboard Mappe Interattive con Tooltip")

# Sidebar per selezione
with st.sidebar:
    st.header("Configurazione")
    
    # Opzione per caricare dati o usare esempi
    data_source = st.radio(
        "Fonte dati",
        ("Carica file GeoJSON", "Usa dati di esempio")
    )
    
    if data_source == "Carica file GeoJSON":
        uploaded_file = st.file_uploader("Carica file GeoJSON", type=["geojson", "json"])
        if uploaded_file is not None:
            map_option = "Dati caricati"
        else:
            map_option = None
    else:
        map_option = st.selectbox(
            "Seleziona la mappa da visualizzare",
            ("Quartieri", "Unità Urbanistiche", "Municipi")
        )
    
    # Campo da visualizzare
    value_field = st.text_input("Campo per i valori (colora la mappa)", "value")
    
    # Opzioni aggiuntive
    show_labels = st.checkbox("Mostra etichette", value=True)
    map_style = st.selectbox(
        "Stile mappa",
        ("OpenStreetMap", "Stamen Terrain", "Stamen Toner", "CartoDB positron")
    )

# Funzione per creare mappe con Folium
def create_map(geo_data, data_field="name", value_field="value", tooltip_fields=None, title=""):
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
        if value_field in geo_data.columns:
            colormap = linear.YlOrRd_09.scale(
                geo_data[value_field].min(),
                geo_data[value_field].max()
            )
            
            # Aggiungi la legenda
            colormap.caption = value_field.capitalize()
            m.add_child(colormap)
            
            # Aggiungi il layer GeoJSON
            folium.GeoJson(
                geo_json_data,
                name=title,
                style_function=lambda feature: {
                    'fillColor': colormap(feature['properties'][value_field]) if value_field in feature['properties'] else '#3388ff',
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
        else:
            # Se il campo valore non esiste, mostra solo le geometrie
            folium.GeoJson(
                geo_json_data,
                name=title,
                style_function=lambda feature: {
                    'fillColor': '#3388ff',
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
        if show_labels and data_field in geo_data.columns:
            for idx, row in geo_data.iterrows():
                # Prendi il centroide della geometria
                centroid = row.geometry.centroid
                # Aggiungi un marker con etichetta
                label_text = str(row.get(data_field, idx))
                folium.Marker(
                    [centroid.y, centroid.x],
                    icon=folium.DivIcon(
                        icon_size=(150, 36),
                        icon_anchor=(75, 18),
                        html=f'<div style="font-size: 10pt; color: black; text-align: center;">{label_text}</div>'
                    )
                ).add_to(m)
    
    return m

# Funzione per caricare i dati
@st.cache_data
def load_data(option=None, uploaded_file=None):
    """
    Carica dati da file caricato o genera dati di esempio.
    """
    if uploaded_file is not None:
        # Carica dati dal file caricato
        try:
            # Leggi il file GeoJSON
            gdf = gpd.read_file(uploaded_file)
            return gdf
        except Exception as e:
            st.error(f"Errore nel caricamento del file: {e}")
            return None
    
    # Altrimenti carica dati di esempio
    if option is None:
        return None
        
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
if data_source == "Carica file GeoJSON" and uploaded_file is not None:
    geo_data = load_data(uploaded_file=uploaded_file)
    if geo_data is not None:
        st.sidebar.success(f"File caricato con successo! Colonne disponibili: {', '.join(geo_data.columns)}")
        
        # Se l'utente ha inserito un campo per i valori che non esiste, avvisa
        if value_field not in geo_data.columns:
            st.sidebar.warning(f"Il campo '{value_field}' non esiste nei dati. Seleziona un campo tra: {', '.join(geo_data.columns)}")
elif map_option is not None:
    geo_data = load_data(option=map_option)
else:
    st.warning("Seleziona una fonte dati o carica un file GeoJSON.")
    geo_data = None

# Crea la mappa se abbiamo dati
if geo_data is not None:
    # Determina quali campi sono disponibili per i tooltip
    available_fields = [col for col in geo_data.columns if col != 'geometry']
    
    # Identifica il campo per il nome/etichetta (preferisci 'name' se esiste)
    label_field = 'name' if 'name' in geo_data.columns else available_fields[0]
    
    # Crea la mappa
    m = create_map(
        geo_data, 
        data_field=label_field, 
        value_field=value_field,
        tooltip_fields=available_fields, 
        title=map_option if map_option else "Dati caricati"
    )
else:
    # Crea una mappa vuota
    m = folium.Map(
        location=[44.4949, 11.3426],  # Bologna, Italia
        zoom_start=12,
        tiles=map_style
    )

# Layout della dashboard
col1, col2 = st.columns([3, 1])

with col1:
    # Mostra la mappa
    if map_option:
        st.subheader(f"Mappa {map_option}")
    else:
        st.subheader("Mappa dai dati caricati")
    folium_static(m, width=800, height=600)

with col2:
    # Mostra statistiche e informazioni solo se abbiamo dati
    if geo_data is not None:
        st.subheader("Statistiche")
        
        # Mostra una tabella con i dati (escludendo la geometria)
        columns_to_show = [col for col in geo_data.columns if col != 'geometry']
        st.dataframe(geo_data[columns_to_show])
        
        # Aggiungi alcuni grafici se abbiamo i campi necessari
        if value_field in geo_data.columns:
            st.subheader(f"Grafico {value_field}")
            
            # Determina il campo indice per il grafico
            index_field = 'name' if 'name' in geo_data.columns else geo_data.columns[0]
            if index_field != 'geometry':
                st.bar_chart(geo_data.set_index(index_field)[value_field])
        
        # Mostra altri grafici se abbiamo i campi
        for field in ['population', 'density', 'area']:
            if field in geo_data.columns:
                st.subheader(f"Distribuzione {field}")
                
                # Determina il campo indice per il grafico
                index_field = 'name' if 'name' in geo_data.columns else geo_data.columns[0]
                if index_field != 'geometry':
                    st.bar_chart(geo_data.set_index(index_field)[field])
    else:
        st.info("Carica un file GeoJSON o seleziona dati di esempio per vedere le statistiche.")

# Aggiungi note e istruzioni
st.markdown("---")
st.markdown("""
### Istruzioni:
1. Per usare i tuoi dati, seleziona "Carica file GeoJSON" nella barra laterale e carica il tuo file
2. Puoi personalizzare quale campo usare per i valori (colore della mappa)
3. Attiva/disattiva le etichette o cambia lo stile della mappa dalla barra laterale
""")

# Mostra istruzioni per il formato dei dati
with st.expander("Formato dei dati supportato"):
    st.markdown("""
    ### Formato GeoJSON
    L'applicazione supporta file GeoJSON con il seguente formato:
    ```json
    {
      "type": "FeatureCollection",
      "features": [
        {
          "type": "Feature",
          "properties": {
            "name": "Nome area",
            "value": 123,
            "population": 45678,
            ... altri attributi ...
          },
          "geometry": {
            "type": "Polygon",
            "coordinates": [[[x1, y1], [x2, y2], ...]]
          }
        },
        ... altre aree ...
      ]
    }
    ```
    
    ### Colonne consigliate
    - `name`: Il nome dell'area (per etichette)
    - `value`: Un valore numerico per colorare la mappa
    - `population`: Popolazione dell'area
    - Altre colonne verranno mostrate nei tooltip e nella tabella
    """)

# Mostra informazioni sull'ambiente
st.sidebar.markdown("---")
st.sidebar.info("""
### Requisiti:
- streamlit==1.36.0
- folium==0.15.1
- streamlit-folium==0.18.0
- pandas==2.2.1
- geopandas==0.14.3
- shapely==2.0.2
- branca==0.7.1
""")
