import streamlit as st
import pandas as pd

# GitHub Excel failo nuoroda
LIKUCIAI_URL = "https://github.com/VadimasBeersteinas/Uzsakymu_valdymas/raw/main/likučiai.xlsx"

@st.cache_data
def load_data(url):
    """ Nuskaito Excel failą ir apdoroja duomenis. """
    try:
        df = pd.read_excel(url, engine='openpyxl')  # Naudojame `openpyxl`, kad būtų suderinamas su `.xlsx`
        df.columns = ["Kiekis", "Prekė"]  # Užtikriname teisingus stulpelių pavadinimus
        return df
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant Excel failą: {e}")
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
