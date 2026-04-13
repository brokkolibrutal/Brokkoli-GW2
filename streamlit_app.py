import streamlit as st
import requests
import pandas as pd

# Konfiguration der Seite
st.set_page_config(page_title="GW2 Himmlischer Preis-Monitor", layout="wide")

def format_gw2_price(coins):
    if not coins or coins == 0: return "Nicht gelistet"
    gold = coins // 10000
    silver = (coins % 10000) // 100
    copper = coins % 100
    # Nutze Fettschrift für bessere Lesbarkeit (wie Gold/Silber im Spiel)
    return f"**{gold}g {silver}s {copper}c**"

st.title("🛡️ GW2 Preis-Monitor: Himmlische Rüstung")
st.markdown("Aktuelle Preise aus dem Handelsposten für **exotische** Ausrüstung mit himmlischen Werten.")

# Item-IDs für die deutschen Sets
# Leicht: Gelehrter, Mittel: Abenteurer, Schwer: Ritter
items_dict = {
    "Leichte Rüstung (Gelehrter)": [11504, 11506, 11501, 11502, 11505, 11503],
    "Mittlere Rüstung (Abenteurer)": [11639, 11641, 11636, 11637, 11640, 11638],
    "Schwere Rüstung (Ritter)": [11891, 11893, 11888, 11889, 11892, 11890],
    "Tornister (Rücken)": [23045, 23044, 23046] # Leder, Stoff, Schuppen
}

# Alle IDs sammeln
all_ids = [idx for sublist in items_dict.values() for idx in sublist]
ids_str = ",".join(map(str, all_ids))

# API Abfrage mit dem Sprachparameter lang=de
@st.cache_data(ttl=300) # 5 Minuten Cache, schont die API
def get_gw2_data(ids):
    # Preise brauchen keinen Sprachparameter (nur Zahlen)
    prices = requests.get(f"https://api.guildwars2.com/v2/commerce/prices?ids={ids}").json()
    # Items mit lang=de für deutsche Namen
    items = requests.get(f"https://api.guildwars2.com/v2/items?ids={ids}&lang=de").json()
    return items, prices

if st.button('Preise aktualisieren'):
    try:
        items_data, prices_data = get_gw2_data(ids_str)
        
        # Mapping erstellen
        price_map = {p['id']: p for p in prices_data}
        item_map = {i['id']: i for i in items_data}

        tabs = st.tabs(list(items_dict.keys()))

        for tab, (category, ids) in zip(tabs, items_dict.items()):
            with tab:
                category_list = []
                for item_id in ids:
                    if item_id in item_map and item_id in price_map:
                        item = item_map[item_id]
                        price = price_map[item_id]
                        
                        category_list.append({
                            "Icon": item['icon'],
                            "Name": item['name'],
                            "Sofort-Kauf": format_gw2_price(price['sells']['unit_price']),
                            "Höchstgebot": format_gw2_price(price['buys']['unit_price']),
                            "Verfügbar": price['sells']['quantity']
                        })
                
                df = pd.DataFrame(category_list)
                st.data_editor(
                    df,
                    column_config={
                        "Icon": st.column_config.ImageColumn("Icon", width="small"),
                        "Name": st.column_config.TextColumn("Gegenstand", width="large")
                    },
                    use_container_width=True,
                    key=f"table_{category}",
                    disabled=True # Nur Anzeige, keine Bearbeitung
                )
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
else:
    st.write("Klicke auf den Button, um die aktuellen Marktdaten zu laden.")

st.divider()
st.caption("Hinweis: Himmlische Rüstung ist oft günstiger durch Crafting herzustellen. Diese Preise beziehen sich auf den direkten Kauf im Handelsposten.")