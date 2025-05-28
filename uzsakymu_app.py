import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ------------------------------------------------------------------
# El. pašto siuntimo konfigūracija – naudokite savo saugų būdą išsaugoti šiuos duomenis!
SMTP_SERVER = "smtp.gmail.com"                       
SMTP_PORT = 587                                      
SENDER_EMAIL = "uzsakymaisandeliui@gmail.com"        
SENDER_PASSWORD = "yffbskojzdldkdxa"  # Jūsų sugeneruotas App Password
RECIPIENT_EMAIL = "vadimas.beersteinas@gmail.com"    # Naujas gavėjo el. pašto adresas
# ------------------------------------------------------------------

# Dropbox Excel failo nuoroda (Direct Link)
LIKUCIAI_URL = "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0"

# Prisijungimo duomenys (vienas bendras vartotojas)
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
            st.rerun()  # Perkrauna puslapį, kad įsigaliuotų nauja būsena
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

# Funkcija, siunčianti užsakymo sąrašą el. paštu
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
    st.title("📦 Užsakymų sistema")
    
    # Mygtukas atsijungimui (visada matomas viršuje)
    if st.button("Atsijungti"):
        st.session_state.pop("authenticated")
        st.rerun()
    
    df = load_data(LIKUCIAI_URL)

    if "Prekė" in df.columns and not df.empty:
        # Inicializuojame užsakymų sąrašą, jei dar nėra
        if "orders" not in st.session_state:
            st.session_state.orders = []

        st.subheader("Pridėti prekę į užsakymą")
        pasirinkta_prekė = st.selectbox("Pasirinkite prekę", df["Prekė"])
        max_kiekis = int(df[df["Prekė"] == pasirinkta_prekė]["Kiekis"].values[0])
        kiekis = st.number_input("Įveskite kiekį", min_value=1, max_value=max_kiekis, value=1)

        if st.button("➕ Pridėti"):
            st.session_state.orders.append({"Prekė": pasirinkta_prekė, "Kiekis": kiekis})
            st.success(f"Pridėta: {pasirinkta_prekė} – {kiekis} vnt.")

        # Rodome užsakymų sąrašą su galimybe pašalinti įrašą
        if st.session_state.orders:
            st.subheader("Užsakytų prekių sąrašas")
            for idx, order in enumerate(st.session_state.orders):
                col1, col2, col3 = st.columns([3, 3, 1])
                col1.write(f"Prekė: {order['Prekė']}")
                col2.write(f"Kiekis: {order['Kiekis']} vnt.")
                # Minus mygtukas pašalinimui
                if col3.button("–", key=f"remove_{idx}"):
                    st.session_state.orders.pop(idx)
                    st.rerun()  # Perkrauna puslapį po pašalinimo

        # Užsakymo pateikimo mygtukas
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
