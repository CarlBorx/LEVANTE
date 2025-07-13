
import streamlit as st
import pandas as pd
import re

@st.cache_data
def load_data():
    df = pd.read_excel("CARTELLONI_BOLOGNA.xlsx", skiprows=3)
    df = df[["Denominazione", "DAL AL", "Pari_Dispari", "CD Padre"]].rename(columns={
        "Denominazione": "Via",
        "DAL AL": "Intervallo",
        "Pari_Dispari": "Parita",
        "CD Padre": "Zona"
    })
    df = df.dropna(subset=["Via", "Intervallo", "Parita", "Zona"])
    df["Parita"] = df["Parita"].map({0: "Pari", 1: "Dispari"})
    df["Via"] = df["Via"].str.upper().str.strip()

    intervalli = []
    for _, row in df.iterrows():
        via, zona, parita, text = row["Via"], row["Zona"], row["Parita"], row["Intervallo"]
        for blocco in text.split(","):
            match_dal = re.search(r"dal\s+(\d+)", blocco)
            match_al = re.search(r"al\s+(\d+)", blocco)
            if match_dal and match_al:
                try:
                    da = int(re.sub(r"\D", "", match_dal.group(1)))
                    a = int(re.sub(r"\D", "", match_al.group(1)))
                    intervalli.append({
                        "Via": via,
                        "Zona": zona,
                        "Parita": parita,
                        "Civico_Da": da,
                        "Civico_A": a
                    })
                except:
                    pass
    return pd.DataFrame(intervalli)

def normalizza_via(via):
    via = via.upper().strip()
    via = re.sub(r"[^A-Z0-9 ]", "", via)
    parole = via.split()
    return " ".join(sorted(parole))

def normalizza_civico(civico):
    match = re.match(r"(\d+)", str(civico))
    return int(match.group(1)) if match else None

def trova_zona(df, via_input, civico_input):
    via_input = normalizza_via(via_input)
    civico = normalizza_civico(civico_input)
    parita = "Pari" if civico % 2 == 0 else "Dispari"
    risultati = df[df["Parita"] == parita].copy()
    risultati["Via_norm"] = risultati["Via"].apply(normalizza_via)
    risultati = risultati[risultati["Via_norm"] == via_input]
    risultati = risultati[(risultati["Civico_Da"] <= civico) & (risultati["Civico_A"] >= civico)]
    return risultati["Zona"].unique()

def trova_zone_per_via(df, via_input):
    via_input = normalizza_via(via_input)
    df["Via_norm"] = df["Via"].apply(normalizza_via)
    risultati = df[df["Via_norm"] == via_input]
    return risultati[["Zona", "Parita", "Civico_Da", "Civico_A"]].drop_duplicates()

st.set_page_config(page_title="Ricerca Zone Bologna", layout="centered")
st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        h1 { color: #0033a0; }
        .stButton>button { background-color: #ffd700; color: black; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📍 Ricerca Zona per Via e Civico - Bologna")

via_input = st.text_input("Inserisci il nome della via:").strip()
civico_input = st.text_input("Inserisci il numero civico (opzionale):").strip()

df = load_data()

if via_input:
    if civico_input:
        zona = trova_zona(df, via_input, civico_input)
        if len(zona):
            st.success(f"✅ Zona trovata: {zona[0]}")
        else:
            st.error("❌ Nessuna zona trovata per questa via e civico.")
    else:
        st.info("🔍 Risultati per la via:")
        zone_df = trova_zone_per_via(df, via_input)
        if not zone_df.empty:
            st.dataframe(zone_df)
        else:
            st.warning("Nessuna zona trovata per questa via.")
