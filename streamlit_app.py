import streamlit as st
import requests
import pandas as pd

# Konfiguration der Seite
st.set_page_config(page_title="GW2 Himmlisch Prunkvoll Monitor", layout="wide")

def format_gw2_price(coins):
    if not coins or coins == 0: return "Nicht gelistet"
    gold = coins // 10000
    silver = (coins % 10000) // 100
    copper = coins % 100
    return f"**{gold}g {silver}s {copper}c**"

st.title("🛡️ GW2 Preis-Monitor: Himmlisch Prunkvoll")
st.markdown("Anzeige der Preise für **Himmlisch Prunkvolle** (Leicht), **Prunkvolle** (Mittel/Schwer) Exotische Sets.")

# Item-IDs für die "Prunkvollen" Sets (Exotisch, Stufe 80, Himmlisch)
items_dict = {
    "Leicht (Himmlisch Prunkvoll)": [43788, 43789, 43785, 43786, 43790, 43787],
    "Mittel (Himmlisch Prunkvoll)": [43794, 43795, 43791, 43792, 43796, 43793],
    "Schwer (Himmlisch Prunkvoll)": [43800, 43801, 43797, 43798, 43802, 43799],
    "Tornister (Rücken)": [23045, 23044, 23046]

# Alle IDs sammeln
all_ids = [idx for sublist in items_dict.values() for idx in sublist]
ids_str = ",".join(map(str, all_ids))

@st.cache_data(ttl=300)
def get_gw2_data(ids):
    # Preise abrufen
    prices_res = requests.get(f"https://api.guildwars2.com/v2/commerce/prices?ids={ids}")
    # Items abrufen mit lang=de für deutsche Namen
    items_res = requests.get(f"https://api.guildwars2.com/v2/items?ids={ids}&lang=de")
    
    return items_res.json(), prices_res.json()

if st.button('Preise jetzt aktualisieren'):
    try:
        items_data, prices_data = get_gw2_data(ids_str)
        
        # Mapping erstellen für schnellen Zugriff
        price_map = {p['id']: p for p in prices_data}
        item_map = {i['id']: i for i in items_data}

        tabs = st.tabs(list(items_dict.keys()))

        for tab, (category, ids) in zip(tabs, items_dict.items()):
            with tab:
                category_list = []
                total_sell_price = 0
                
                for item_id in ids:
                    if item_id in item_map and item_id in price_map:
                        item = item_map[item_id]
                        price = price_map[item_id]
                        unit_price = price['sells']['unit_price']
                        total_sell_price += unit_price
                        
                        category_list.append({
                            "Icon": item['icon'],
                            "Name": item['name'],
                            "Sofort-Kauf": format_gw2_price(unit_price),
                            "Höchstgebot": format_gw2_price(price['buys']['unit_price']),
                            "Bestand": price['sells']['quantity']
                        })
                
                # Tabelle anzeigen
                df = pd.DataFrame(category_list)
                st.data_editor(
                    df,
                    column_config={
                        "Icon": st.column_config.ImageColumn(" ", width="small"),
                        "Name": st.column_config.TextColumn("Gegenstand", width="large")
                    },
                    use_container_width=True,
                    key=f"table_{category}",
                    disabled=True,
                    hide_index=True
                )
                
                # Zusammenfassung der Set-Kosten
                if category != "Tornister (Rücken)":
                    st.metric("Gesamtkosten für dieses Set (Sofort-Kauf)", format_gw2_price(total_sell_price).replace("*", ""))

    except Exception as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")
else:
    st.info("Bitte Button klicken, um die deutschen Item-Daten zu laden.")

st.divider()
st.caption("Datenquelle: Offizielle GW2 API | Sprache: Deutsch")
