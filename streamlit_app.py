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
    "Leicht (Himmlisch Prunkvoll)": [11504, 11506, 11501, 11502, 11505, 11503],
    "Mittel (Himmlisch Prunkvoll)": [11639, 11641, 11636, 11637, 11640, 11638],
    "Schwer (Himmlisch Prunkvoll)": [11891, 11893, 11888, 11889, 11892, 11890],
    "Tornister (Rücken)": [23045, 23044, 23046]
}

# Alle IDs sammeln
all_ids = [idx for sublist in items_dict.values() for idx in sublist]
ids_str = ",".join(map(str, all_ids))

@st.cache_data(ttl=300)
def get_gw2_data(ids):
    # Preise abrufen
    prices_res = requests.get(f"https://api.guildwars2.com/v2/commerce/prices?ids={ids}")
    # Items abrufen mit