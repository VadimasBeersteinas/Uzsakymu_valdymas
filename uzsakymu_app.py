import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Dropbox Excel failo nuoroda (pakeisk į savo „direct link“!)
LIKUCIU_URL = "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0"

def load_data(url):
    """ Atsisiunčia Excel failą iš Dropbox ir apdoroja duomenis """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"❌ Nepavyko atsisiųsti failo. Statusas: {response.status_code}")
            return pd.DataFrame(columns=["Kiekis", "Prekė"])
        
        df = pd.read_excel(BytesIO(response.content), engine='openpyxl', usecols=["I17_kiekis      ", "P_pav                                                                                                                   "])
        df.columns = ["Kiekis", "Prekė"]
        return df
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant failą: {e}")
        return pd.DataFrame(columns=["Kiekis", "Prekė"])

# Nuskaitome duomenis
df = load_data(LIKUCIU_URL)

# Streamlit UI
st.title("📦 Užsakymų sistema")

if 'Prekė' in df.columns and not df.empty:
    pasirinkta_prekė = st.selectbox("Pasirinkite prekę", df["Prekė"])
    max_kiekis = int(df[df["Prekė"] == pasirinkta_prekė]["Kiekis"].values[0])
    kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis)

    if st.button("✅ Pateikti užsakymą"):
        st.subheader("✅ Užsakymas pateiktas!")
        st.write(f"Prekė: **{pasirinkta_prekė}**")
        st.write(f"Kiekis: **{kiekis} vnt.**")

else:
    st.error("⚠️ Faile 'likučiai.xlsx' nėra tinkamų duomenų arba jis nepavyko nuskaityti.")
