import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Dropbox Excel failo nuoroda (Direct Link)
LIKUCIAI_URL = "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0"

# Prisijungimo duomenys
USERNAME = "MANIGA"
PASSWORD = "Maniga_sirpučių"

# Prisijungimo funkcija
def login():
    st.title("🔒 Prisijungimas")
    username = st.text_input("Vartotojo vardas")
    password = st.text_input("Slaptažodis", type="password")

    if st.button("✅ Prisijungti"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Perkrauna puslapį, kad įsigaliuotų autentifikacijos būsena
        else:
            st.error("❌ Neteisingas vartotojo vardas arba slaptažodis!")

# Duomenų nuskaitymo funkcija su naujuoju caching dekoratoriumi
@st.cache_data
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"❌ Nepavyko atsisiųsti failo. HTTP kodas: {response.status_code}")
            return pd.DataFrame(columns=["Kiekis", "Prekė"])
        
        df = pd.read_excel(
            BytesIO(response.content),
            engine='openpyxl',
            usecols=["I17_kiekis      ", "P_pav                                                                                                                   "]
        )
        df.columns = ["Kiekis", "Prekė"]
        return df
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant failą: {e}")
        return pd.DataFrame(columns=["Kiekis", "Prekė"])

def main():
    st.title("📦 Užsakymų sistema")
    df = load_data(LIKUCIAI_URL)

    if 'Prekė' in df.columns and not df.empty:
        # Inicializuojame užsakymų sąrašą, jei dar nėra
        if "orders" not in st.session_state:
            st.session_state.orders = []

        st.subheader("Pridėti prekę į užsakymą")
        pasirinkta_prekė = st.selectbox("Pasirinkite prekę", df["Prekė"])
        max_kiekis = int(df[df["Prekė"] == pasirinkta_prekė]["Kiekis"].values[0])
        kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis, value=1)

        # Mygtukas prekių pridėjimui
        if st.button("➕ Pridėti"):
            st.session_state.orders.append({"Prekė": pasirinkta_prekė, "Kiekis": kiekis})
            st.success(f"Pridėta: {pasirinkta_prekė} – {kiekis} vnt.")

        # Jei nors viena prekė užsakyta – rodyti dabartinį užsakymų sąrašą
        if st.session_state.orders:
            st.subheader("Užsakytų prekių sąrašas")
            st.table(pd.DataFrame(st.session_state.orders))

        # Užsakymo pateikimo mygtukas
        if st.button("✅ Pateikti užsakymą"):
            st.subheader("✅ Užsakymas pateiktas!")
            st.table(pd.DataFrame(st.session_state.orders))
            # Galite, jei reikia, išvalyti užsakymų sąrašą po pateikimo:
            # st.session_state.orders = []
    else:
        st.error("⚠️ Faile 'likučiai.xlsx' nėra tinkamų duomenų arba jis nepavyko nuskaityti.")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    login()
else:
    main()
