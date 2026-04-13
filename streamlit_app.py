import streamlit as st
import requests
import pandas as pd

# Funktion zum Umrechnen der GW2-Währung (Coins)
def format_gw2_price(coins):
    if coins == 0: return "0 c"
    gold = coins // 10000
    silver = (coins % 10000) // 100
    copper = coins % 100
    
    parts = []
    if gold > 0: parts.append(f"{gold}g")
    if silver > 0: parts.append(f"{silver}s")
    if copper > 0: parts.append(f"{copper}c")
    return " ".join(parts)

st.title("GW2 Preis-Monitor 1️⃣2️⃣3️⃣")

# Liste der Item-IDs (Beispiele: Ektoplasmakugel, Legendäre, etc.)
# IDs findest du auf dem GW2 Wiki oder Seiten wie GW2TP
item_ids = [19721, 19684, 30688, 30698] 

if st.button('Preise aktualisieren'):
    ids_str = ",".join(map(str, item_ids))
    
    # 1. Preisdaten holen
    price_url = f"https://api.guildwars2.com/v2/commerce/prices?ids={ids_str}"
    prices = requests.get(price_url).json()
    
    # 2. Item-Details (Namen) holen
    item_url = f"https://api.guildwars2.com/v2/items?ids={ids_str}"
    items = requests.get(item_url).json()
    
    # Daten zusammenführen
    display_data = []
    for p in prices:
        # Finde den passenden Namen aus der Items-Liste
        item_info = next(i for i in items if i['id'] == p['id'])
        
        display_data.append({
            "Icon": item_info['icon'],
            "Name": item_info['name'],
            "Verkauf (Sell)": format_gw2_price(p['sells']['unit_price']),
            "Kauf (Buy)": format_gw2_price(p['buys']['unit_price']),
            "Menge (Verkauf)": p['sells']['quantity']
        })

    # Tabelle anzeigen
    df = pd.DataFrame(display_data)
    st.data_editor(df, column_config={
        "Icon": st.column_config.ImageColumn("Icon")
    }, use_container_width=True)