import streamlit as st
import requests
import pandas as pd

# Konfiguration der Seite
st.set_page_config(page_title="GW2 Celestial Price Monitor", layout="wide")

def format_gw2_price(coins):
    if not coins or coins == 0: return "Nicht gelistet"
    gold = coins // 10000
    silver = (coins % 10000) // 100
    copper = coins % 100
    return f"{gold}g {silver}s {copper}c"

st.title("🛡️ GW2 Preis-Monitor: Himmlische Rüstung")
st.info("Zeigt die aktuellen Handelsposten-Preise für exotische himmlische Ausrüstung.")

# Item-IDs nach Kategorien
items_dict = {
    "Leicht (Gelehrter)": [11504, 11506, 11501, 11502, 11505, 11503],
    "Mittel (Abenteurer)": [11639, 11641, 11636, 11637, 11640, 11638],
    "Schwer (Ritter)": [11891, 11893, 11888, 11889, 11892, 11890],
    "Rücken (Tornister)": [23045] # Beispiel: Handgefertigter Leder-Tornister (Himmlische Werte)
}

# Alle IDs in eine flache Liste für die API-Abfrage
all_ids = [idx for sublist in items_dict.values() for idx in sublist]

if st.button('Preise jetzt aktualisieren'):
    ids_str = ",".join(map(str, all_ids))
    
    # API Abfragen
    try:
        prices_data = requests.get(f"https://api.guildwars2.com/v2/commerce/prices?ids={ids_str}").json()
        items_data = requests.get(f"https://api.guildwars2.com/v2/items?ids={ids_str}").json()
        
        # Mapping erstellen
        price_map = {p['id']: p for p in prices_data}
        item_map = {i['id']: i for i in items_data}

        # Tabs für die Übersichtlichkeit
        tabs = st.tabs(list(items_dict.keys()))

        for tab, (category, ids) in zip(tabs, items_dict.items()):
            with tab:
                category_data = []
                for item_id in ids:
                    if item_id in item_map and item_id in price_map:
                        item = item_map[item_id]
                        price = price_map[item_id]
                        
                        category_data.append({
                            "Icon": item['icon'],
                            "Name": item['name'],
                            "Sofort-Verkauf": format_gw2_price(price['sells']['unit_price']),
                            "Höchstgebot (Kauf)": format_gw2_price(price['buys']['unit_price']),
                            "Angebotene Menge": price['sells']['quantity']
                        })
                
                df = pd.DataFrame(category_data)
                st.data_editor(
                    df,
                    column_config={"Icon": st.column_config.ImageColumn("Icon")},
                    use_container_width=True,
                    key=f"table_{category}"
                )
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")

st.divider()
st.caption("Daten kommen direkt aus der offiziellen Guild Wars 2 API.")