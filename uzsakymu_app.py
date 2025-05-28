import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import smtplib
from email.message import EmailMessage

# ------------------------------------------------------------------
# El. pašto siuntimo konfigūracija
SMTP_SERVER = "smtp.gmail.com"                       
SMTP_PORT = 587                                      
SENDER_EMAIL = "uzsakymaisandeliui@gmail.com"        
SENDER_PASSWORD = "yffbskojzdldkdxa"  
RECIPIENT_EMAIL = "vadimas.beersteinas@gmail.com"    
# ------------------------------------------------------------------

LIKUCIAI_URL = (
    "https://dl.dropboxusercontent.com/scl/fi/82mr72rih8bqjz33tm1he/liku-iai.xlsx?"
    "rlkey=wh7tsy06woxbmuurt9hw3b6s2&st=j1qhh1ac&dl=0"
)

USERNAME = "MANIGA"
PASSWORD = "Maniga_sirpučių"

def login():
    st.title("🔒 Prisijungimas")
    username = st.text_input("Vartotojo vardas")
    password = st.text_input("Slaptažodis", type="password")
    if st.button("✅ Prisijungti"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
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

def send_order_via_email(order_list, from_location, to_location):
    message_content = f"Naujas užsakymas:\n\nIš objekto: {from_location}\nĮ objektą: {to_location}\n\n"
    for order in order_list:
        message_content += f"Prekė: {order['Prekė']} | Kiekis: {order['Kiekis']} vnt.\n"

    msg = EmailMessage()
    msg.set_content(message_content)
    msg["Subject"] = "Naujas užsakymas"
    msg["From"] =
