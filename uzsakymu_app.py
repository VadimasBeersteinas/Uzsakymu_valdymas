import streamlit as st
import pandas as pd

# GitHub failo nuoroda
LIKUCIAI_URL = "https://github.com/VadimasBeersteinas/Uzsakymu_valdymas/raw/refs/heads/main/liku%C4%8Diai.xlsx"

# Nuskaitome prekių likučius
try:
    df = pd.read_excel(LIKUCIAI_URL, usecols=["I17_kiekis", "P_pav"])
    df.columns = ["Kiekis", "Prekė"]
except Exception as e:
    st.error("❌ Klaida nuskaitant failą iš GitHub! Įsitikinkite, kad nuoroda teisinga.")

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
