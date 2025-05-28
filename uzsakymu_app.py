import streamlit as st
import pandas as pd
import requests

# GitHub CSV failo nuoroda
LIKUCIAI_URL = "https://raw.githubusercontent.com/VadimasBeersteinas/Uzsakymu_valdymas/main/likučiai.csv"

def check_url(url):
    """ Patikriname, ar failas egzistuoja GitHub. """
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"❌ Nepavyko pasiekti CSV failo. HTTP statusas: {response.status_code}")
        return False
    return True

@st.cache_data
def load_data(url):
    """ Nuskaito ir apdoroja CSV failą, pritaikant skyriklį ir kodavimą. """
    if not check_url(url):
        return pd.DataFrame(columns=["Kiekis", "Prekė"])
    
    try:
        # Bandome įvairius nustatymus nuskaitymui
        for encoding in ["utf-8", "utf-8-sig", "ISO-8859-1"]:
            for sep in [",", ";", "\t"]:
                try:
                    df = pd.read_csv(url, encoding=encoding, sep=sep)
                    if df.shape[1] == 2:  # Patikriname, ar yra tik 2 stulpeliai
                        df.columns = ["Kiekis", "Prekė"]
                        return df
                except Exception:
                    pass
        
        st.error("❌ Nepavyko tinkamai nuskaityti CSV failo. Patikrinkite skyriklį ir kodavimą.")
        return pd.DataFrame(columns=["Kiekis", "Prekė"])
    
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant failą: {e}")
        return pd.DataFrame(columns=["Kiekis", "Prekė"])

# Nuskaitome prekių likučius
df = load_data(LIKUCIAI_URL)

# Streamlit UI
st.title("📦 Užsakymų sistema")

if df.empty:
    st.warning("⚠️ Duomenų lentelė tuščia arba nepavyko nuskaityti failo!")
else:
    # Prekės pasirinkimas
    selected_item = st.selectbox("Pasirinkite prekę", df["Prekė"].tolist())
    max_kiekis = int(df[df["Prekė"] == selected_item]["Kiekis"].values[0])
    selected_kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis)

    # Užsakymų saugojimas sesijoje
    if "orders" not in st.session_state:
        st.session_state.orders = []

    # Pridėti prekę
    if st.button("➕ Pridėti"):
        st.session_state.orders.append({"Prekė": selected_item, "Kiekis": selected_kiekis})
        st.success(f"{selected_item} ({selected_kiekis} vnt.) pridėta!")

    # Rodyti sąrašą
    if st.session_state.orders:
        st.subheader("📋 Užsakytų prekių sąrašas")
        st.table(pd.DataFrame(st.session_state.orders))

    # Pateikti užsakymą
    if st.button("✅ Pateikti užsakymą"):
        st.subheader("✅ Užsakymas pateiktas!")
        st.table(pd.DataFrame(st.session_state.orders))
        st.session_state.orders = []
