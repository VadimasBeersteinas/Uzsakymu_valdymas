import streamlit as st
import pandas as pd
import requests
import tempfile

# GitHub CSV failo nuoroda
LIKUCIAI_URL = "https://github.com/VadimasBeersteinas/Uzsakymu_valdymas/blob/main/likučiai.csv"

# Atsisiunčiame failą į laikiną vietą ir nuskaitome jį
try:
    response = requests.get(LIKUCIAI_URL)
    response.raise_for_status()  # Patikrina, ar atsisiuntimas buvo sėkmingas

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(response.content)
        temp_path = temp_file.name

    df = pd.read_csv(temp_path)
    df.columns = ["Kiekis", "Prekė"]  # Užtikriname teisingus stulpelių pavadinimus
except Exception as e:
    st.error("❌ Klaida nuskaitant failą iš GitHub! Patikrinkite, ar nuoroda teisinga.")

# Streamlit UI
st.title("📦 Užsakymų sistema")

# Pasirinkimo laukeliai
selected_item = st.selectbox("Pasirinkite prekę", df["Prekė"].tolist())
max_kiekis = int(df[df["Prekė"] == selected_item]["Kiekis"].values[0])
selected_kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis)

# Laikinas užsakymų sąrašas sesijoje
if "orders" not in st.session_state:
    st.session_state.orders = []

# Mygtukas pridėti prekę į sąrašą
if st.button("➕ Pridėti"):
    st.session_state.orders.append({"Prekė": selected_item, "Kiekis": selected_kiekis})
    st.success(f"{selected_item} ({selected_kiekis} vnt.) pridėta!")

# Rodomas pasirinktas prekių sąrašas
if st.session_state.orders:
    st.subheader("📋 Užsakytų prekių sąrašas")
    st.table(pd.DataFrame(st.session_state.orders))

# Mygtukas pateikti užsakymą
if st.button("✅ Pateikti užsakymą"):
    st.subheader("✅ Užsakymas pateiktas!")
    st.write("Toliau pateiktos užsakytos prekės:")
    st.table(pd.DataFrame(st.session_state.orders))
    st.session_state.orders = []  # Išvalome sąrašą po užsakymo
