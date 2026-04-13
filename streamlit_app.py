import streamlit as st
import requests
import pandas as pd

# Konfiguration der Seite (Wide Mode für bessere Tabellenansicht)
st.set_page_config(page_title="GW2 Celestial Monitor", layout="wide", page_icon="🛡️")

def format_gw2_price_fancy(coins):
    """Wandelt Coins in Gold, Silber, Kupfer mit Symbolen um."""
    if not coins or coins == 0: 
        return "---"
    
    gold = coins // 10000
    silver = (coins % 10000) // 100
    copper = coins % 100
    
    parts = []
    if gold > 0:
        parts.append(f"{gold} 🟡")
    if silver > 0:
        parts.append(f"{silver} ⚪")
    if copper > 0 or not parts:
        parts.append(f"{copper} 🟤")
        
    return " ".join(parts)

# --- ITEM KONFIGURATION ---
# Deine korrigierten IDs für Schwer (Drakonisch) sind hier enthalten!
items_dict = {
    "Leicht (Erhaben)": [43788, 43789, 43791, 43786, 43790, 43787],
    "Mittel (Prunkvoll)": [43794, 43795, 43797, 43792, 43796, 43793],
    "Schwer (Drakonisch)": [43782, 43784, 43783, 43781, 43783, 43780],
    "Tornister & Zubehör": [43778, 43773, 23045, 23046]
}

# Flache Liste aller IDs für die API-Abfrage
all_ids = [idx for sublist in items_dict.values() for idx in sublist]

st.title("🛡️ GW2 Rüstungs-Monitor")
st.markdown(f"Verfolgt die aktuellen Marktpreise für deine Sets auf **Deutsch**.")

# --- DATENABFRAGE ---
@st.cache_data(ttl=300)
def get_api_data(ids):
    ids_str = ",".join(map(str, ids))
    # Items mit lang=de für deutsche Namen
    items = requests.get(f"https://api.guildwars2.com/v2/items?ids={ids_str}&lang=de").json()
    # Preise vom Handelsposten
    try:
        prices = requests.get(f"https://api.guildwars2.com/v2/commerce/prices?ids={ids_str}").json()
    except:
        prices = []
    return items, prices

if st.button('🔄 Preise jetzt aktualisieren'):
    with st.spinner('Lade Marktdaten...'):
        items_data, prices_data = get_api_data(all_ids)
        
        # Mapping für schnellen Zugriff
        item_map = {i['id']: i for i in items_data}
        price_map = {p['id']: p for p in prices_data}

        # Tabs für die Rüstungsklassen
        tabs = st.tabs(list(items_dict.keys()))

        for tab, (category, ids) in zip(tabs, items_dict.items()):
            with tab:
                display_list = []
                total_set_cost = 0
                
                for item_id in ids:
                    item = item_map.get(item_id, {})
                    price = price_map.get(item_id, {})
                    
                    name = item.get('name', f"ID: {item_id}")
                    icon = item.get('icon', "")
                    
                    sell_raw = price.get('sells', {}).get('unit_price', 0)
                    buy_raw = price.get('buys', {}).get('unit_price', 0)
                    quantity = price.get('sells', {}).get('quantity', 0)
                    
                    if category != "Tornister & Zubehör":
                        total_set_cost += sell_raw

                    display_list.append({
                        "Icon": icon,
                        "Gegenstand": name,
                        "Sofort-Kauf": format_gw2_price_fancy(sell_raw),
                        "Höchstgebot": format_gw2_price_fancy(buy_raw),
                        "Bestand": f"{quantity} Stk."
                    })
                
                # Tabelle anzeigen
                df = pd.DataFrame(display_list)
                st.data_editor(
                    df,
                    column_config={
                        "Icon": st.column_config.ImageColumn("", width="small"),
                        "Gegenstand": st.column_config.TextColumn("Gegenstand", width="large"),
                    },
                    use_container_width=True,
                    hide_index=True,
                    disabled=True,
                    key=f"df_{category}"
                )
                
                # Gesamtpreis-Anzeige für das Set
                if category != "Tornister & Zubehör" and total_set_cost > 0:
                    st.write(f"### 💰 Gesamtwert dieses Sets (Sofort-Kauf): {format_gw2_price_fancy(total_set_cost)}")
else:
    st.info("Klicke auf den Button oben, um die aktuellen Preise aus Tyria zu laden.")

st.divider()
st.caption("Datenquelle: Offizielle Guild Wars 2 API. Die Gold-Symbole werden als Emojis dargestellt.")
