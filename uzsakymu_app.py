import streamlit as st
import pandas as pd

# Failų keliai (Dropbox aplanke tavo kompiuteryje)
LIKUCIAI_PATH = r"C:\Users\DOC\Dropbox\likučiai.xlsx"
UZSAKYMAI_PATH = r"C:\Users\DOC\Dropbox\užsakymai.xlsx"

# Nuskaitome prekių likučius
try:
    df = pd.read_excel(LIKUCIAI_PATH, usecols=["I17_kiekis      ", "P_pav                                                                                                                   "])
    df.columns = ["Kiekis", "Prekė"]
except FileNotFoundError:
    st.error("Failas 'likučiai.xlsx' nerastas. Įsitikinkite, kad kelias teisingas!")

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
    try:
        uzsakymai_df = pd.read_excel(UZSAKYMAI_PATH)
    except FileNotFoundError:
        uzsakymai_df = pd.DataFrame(columns=["Prekė", "Kiekis"])

    # Pridedame užsakytas prekes
    uzsakymai_df = pd.concat([uzsakymai_df, pd.DataFrame(st.session_state.orders)], ignore_index=True)
    uzsakymai_df.to_excel(UZSAKYMAI_PATH, index=False)

    st.success("✅ Užsakymas pateiktas!")
    st.session_state.orders = []  # Išvalome sąrašą po užsakymo

