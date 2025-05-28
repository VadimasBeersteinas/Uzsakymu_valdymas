import streamlit as st
import pandas as pd

# Dropbox Excel failo nuoroda (pakeisk savo failo linką!)
LIKUCIAI_URL = "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0

@st.cache_data
def load_data(url):
    """ Nuskaito Excel failą iš Dropbox """
    try:
        df = pd.read_excel(url, engine='openpyxl')
        df.columns = ["Prekė", "Kiekis"]
        return df
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant failą: {e}")
        return pd.DataFrame(columns=["Prekė", "Kiekis"])

# Nuskaitome duomenis iš Dropbox
df = load_data(LIKUCIAI_URL)

# Streamlit UI
st.title("📦 Užsakymų sistema")

if df.empty:
    st.warning("⚠️ Duomenų lentelė tuščia arba nepavyko nuskaityti failo!")
else:
    selected_item = st.selectbox("Pasirinkite prekę", df["Prekė"].tolist())
    max_kiekis = int(df[df["Prekė"] == selected_item]["Kiekis"].values[0])
    selected_kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis)

    # Užsakymų saugojimas sesijoje
    if "orders" not in st.session_state:
        st.session_state.orders = []

    if st.button("➕ Pridėti"):
        st.session_state.orders.append({"Prekė": selected_item, "Kiekis": selected_kiekis})
        st.success(f"{selected_item} ({selected_kiekis} vnt.) pridėta!")

    if st.session_state.orders:
        st.subheader("📋 Užsakytų prekių sąrašas")
        st.table(pd.DataFrame(st.session_state.orders))
