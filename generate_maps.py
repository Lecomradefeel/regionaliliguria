import folium
import pandas as pd
import json

def generate_map(excel_file, geojson_file, html_output, columns, key_on, tooltip_field, line_color):
    # Carica i dati Excel e pulisci i nomi delle colonne
    df = pd.read_excel(excel_file)
    df.columns = df.columns.str.strip()
    
    # Carica il file GeoJSON
    with open(geojson_file, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Crea una mappa centrata (modifica le coordinate se necessario)
    m = folium.Map(location=[44.4268, 8.8882], zoom_start=12)
    
    # Aggiungi un layer choropleth per visualizzare le percentuali
    folium.Choropleth(
        geo_data=geojson_data,
        data=df,
        columns=columns,  # ad esempio: ["quartiere", "percentuale"]
        key_on=f"feature.properties.{key_on}",  # ad esempio: "quartiere"
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Percentuale"
    ).add_to(m)
    
    # Aggiungi un layer GeoJson con tooltip per mostrare il nome (o altra informazione)
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': line_color,
            'weight': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[tooltip_field],
            aliases=[f"{tooltip_field.capitalize()}: "]
        )
    ).add_to(m)
    
    # Salva la mappa come file HTML
    m.save(html_output)
    print(f"Mappa salvata in {html_output}")

if __name__ == "__main__":
    # Genera la mappa per i Quartieri
    generate_map(
        excel_file="Quartieri con percentuali.xlsx",
        geojson_file="Quartieri.json",
        html_output="map_quartieri.html",
        columns=["quartiere", "percentuale"],
        key_on="quartiere",
        tooltip_field="quartiere",
        line_color="blue"
    )
    
    # Genera la mappa per le Unità Urbanistiche
    generate_map(
        excel_file="UU con percentuali.xlsx",
        geojson_file="Unita_urbanistiche (1).json",
        html_output="map_unita_urbanistiche.html",
        columns=["unita", "percentuale"],
        key_on="unita",
        tooltip_field="unita",
        line_color="green"
    )
    
    # Genera la mappa per i Municipi
    generate_map(
        excel_file="Municipi con percentuali.xlsx",
        geojson_file="Municipi1.json",
        html_output="map_municipi.html",
        columns=["municipio", "percentuale"],
        key_on="municipio",
        tooltip_field="municipio",
        line_color="red"
    )
