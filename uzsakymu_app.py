import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ------------------------------------------------------------------
# El. pašto siuntimo konfigūracija – naudokite savo saugų būdą išsaugoti šiuos duomenis!
SMTP_SERVER = "smtp.gmail.com"                       # Gmail SMTP serveris
SMTP_PORT = 587                                      # TLS prievadas
SENDER_EMAIL = "uzsakymaisandeliui@gmail.com"        # Siuntėjo el. pašto adresas
SENDER_PASSWORD = "yffbskojzdldkdxa"           # Įrašykite čia programos slaptažodį (app password)
RECIPIENT_EMAIL = "vadimas.beersteinas@gmail.com"     # Gavėjo el. pašto adresas  
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
        
        df = pd.read_excel(BytesIO(response.content),
                           engine='openpyxl',
                           usecols=["I17_kiekis      ", "P_pav                                                                                                                   "])
        df.columns = ["Kiekis", "Prekė"]
        return df
    except Exception as e:
        st.error(f"❌ Klaida nuskaitant failą: {e}")
        return pd.DataFrame(columns=["Kiekis", "Prekė"])

# Funkcija, siunčianti užsakymo sąrašą el. paštu
def send_order_via_email(order_list):
    # Sudarome užsakymo turinį
    message_content = "Naujas užsakymas:\n\n"
    for order in order_list:
        message_content += f"Prekė: {order['Prekė']} | Kiekis: {order['Kiekis']} vnt.\n"
    
    # Sukuriame el. laiško objektą
    msg = EmailMessage()
    msg.set_content(message_content)
    msg["Subject"] = "Naujas užsakymas"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Užšifruotas ryšys
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"El. pašto siuntimas nepavyko: {e}")

def main():
    st.title("📦 Užsakymų sistema")
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

        # (Pasirinktine) Rodykite dabartinį užsakymų sąrašą
        if st.session_state.orders:
            st.subheader("Užsakytų prekių sąrašas")
            st.table(pd.DataFrame(st.session_state.orders))

        if st.button("✅ Pateikti užsakymą"):
            try:
                send_order_via_email(st.session_state.orders)
                st.success("✅ Užsakymas sėkmingai išsiųstas į el. paštą!")
                st.session_state.orders = []  # Išvalome sąrašą po siuntimo
            except Exception as e:
                st.error(f"❌ Užsakymo išsiuntimas nepavyko: {e}")
    else:
        st.error("⚠️ Faile 'likučiai.xlsx' nėra tinkamų duomenų arba jis nepavyko nuskaityti.")

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    login()
else:
    main()
