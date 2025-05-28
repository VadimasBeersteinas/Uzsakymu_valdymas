import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ------------------------------------------------------------------
# El. pašto siuntimo konfigūracija – saugiai išsaugokite šiuos duomenis!
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "uzsakymaisandeliui@gmail.com"
SENDER_PASSWORD = "yffbskojzdldkdxa"  # Jūsų sugeneruotas App Password
RECIPIENT_EMAIL = "vadimas.beersteinas@gmail.com"  # Naujas gavėjo el. pašto adresas
# ------------------------------------------------------------------

# Dropbox Excel failo nuoroda (Direct Link)
LIKUCIAI_URL = (
    "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?"
    "rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0"
)

# Prisijungimo duomenys (vienas bendras vartotojas)
USERNAME = "MANIGA"
PASSWORD = "Maniga_sirpučių"

def login():
    st.title("🔒 Prisijungimas")
    username = st.text_input("Vartotojo vardas")
    password = st.text_input("Slaptažodis", type="password")
    if st.button("✅ Prisijungti"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Perkrauna puslapį su nauja būsena
        else:
            st.error("❌ Neteisingas vartotojo vardas arba slaptažodis!")

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

def send_order_via_email(order_list):
    message_content = "Naujas užsakymas:\n\n"
    for order in order_list:
        message_content += f"Prekė: {order['Prekė']} | Kiekis: {order['Kiekis']} vnt.\n"
    msg = EmailMessage()
    msg.set_content(message_content)
    msg["Subject"] = "Naujas užsakymas"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Užšifruotas ryšys
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def main():
    # Minimalus CSS – tik nustatomas padding ir teksto elipsis ląstelėms
    st.markdown("""
    <style>
    .order-cell {
      padding: 5px;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header: pavadinimas kairėje, atsijungimo mygtukas dešinėje
    col_header_left, col_header_right = st.columns([8, 2])
    with col_header_left:
        st.title("📦 Užsakymų sistema")
    with col_header_right:
        if st.button("🚪 Atsijungti", key="logout"):
            st.session_state.pop("authenticated")
            st.rerun()

    df = load_data(LIKUCIAI_URL)
    if "Prekė" in df.columns and not df.empty:
        if "orders" not in st.session_state:
            st.session_state.orders = []

        st.subheader("Pridėti prekę į užsakymą")
        selected_product = st.selectbox("Pasirinkite prekę", df["Prekė"])
        max_qty = int(df[df["Prekė"] == selected_product]["Kiekis"].values[0])
        qty = st.number_input("Įveskite kiekį", min_value=1, max_value=max_qty, value=1)
        if st.button("➕ Pridėti"):
            st.session_state.orders.append({"Prekė": selected_product, "Kiekis": qty})
            st.success(f"Pridėta: {selected_product} – {qty} vnt.")
        
        if st.session_state.orders:
            st.subheader("Užsakytų prekių sąrašas")
            # Lentelės antraštės: panaudojame paprastą HTML, kad tekstas būtų centruotas
            header_cols = st.columns([5, 2, 1])
            header_cols[0].markdown("<p style='padding: 5px; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>Prekė</b></p>", unsafe_allow_html=True)
            header_cols[1].markdown("<p style='padding: 5px; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>Kiekis</b></p>", unsafe_allow_html=True)
            header_cols[2].markdown("<p style='text-align: center; padding: 5px; margin: 0;'><b>Šalinti</b></p>", unsafe_allow_html=True)
            
            # Eilučių su duomenimis rodymas
            for idx, order in enumerate(st.session_state.orders):
                row_cols = st.columns([5, 2, 1])
                row_cols[0].markdown(f"<p class='order-cell'>{order['Prekė']}</p>", unsafe_allow_html=True)
                row_cols[1].markdown(f"<p class='order-cell'>{order['Kiekis']} vnt.</p>", unsafe_allow_html=True)
                with row_cols[2]:
                    # Centruojame mygtuką "-" naudojant HTML paragrafą
                    st.markdown("<p style='text-align: center; margin: 0;'>", unsafe_allow_html=True)
                    if st.button("–", key=f"remove_{idx}"):
                        st.session_state.orders.pop(idx)
                        st.rerun()
                    st.markdown("</p>", unsafe_allow_html=True)
        
        if st.button("✅ Pateikti užsakymą"):
            try:
                send_order_via_email(st.session_state.orders)
                st.success("Užsakymas sėkmingai išsiųstas į el. paštą!")
                st.session_state.orders = []  # Išvalome užsakymų sąrašą
            except Exception as e:
                st.error(f"❌ Užsakymo išsiuntimas nepavyko: {e}")
    else:
        st.error("⚠️ Faile 'likučiai.xlsx' nėra tinkamų duomenų arba jis nepavyko nuskaityti.")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    login()
else:
    main()
