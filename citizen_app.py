# citizen_app.py - Citizen Mobile SOS Interface
import streamlit as st
import requests

st.set_page_config(page_title="ResQ-Grid Citizen SOS", page_icon="🚨", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #fff; }
    .sos-btn {
        background: radial-gradient(circle, #ff003c 0%, #990000 100%);
        border: 3px solid #ff4d6d;
        border-radius: 50%;
        width: 200px;
        height: 200px;
        color: white;
        font-size: 26px;
        font-weight: 800;
        box-shadow: 0 0 35px rgba(255, 0, 60, 0.7);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 ResQ-Grid SOS")
st.caption("Citizen Emergency Distress Transmitter")

name = st.text_input("Your Name / మీ పేరు", value="Ramesh Kumar")
people = st.number_input("Number of People Trapped / చిక్కుకున్న వారి సంఖ్య", min_value=1, max_value=50, value=3)
medical = st.checkbox("🚑 Urgent Medical Assistance Needed (గాయపడినవారు ఉన్నారు)", value=True)

# Coordinates (Default Vijayawada / can be edited or auto-sent)
st.write("📍 **Target Emergency GPS:**")
col_lat, col_lng = st.columns(2)
with col_lat:
    lat = st.number_input("Latitude", value=16.5085, format="%.4f")
with col_lng:
    lng = st.number_input("Longitude", value=80.6520, format="%.4f")

st.write("")
if st.button("🚨 TRANSMIT EMERGENCY SOS 🚨", use_container_width=True):
    payload = {
        "user_name": name,
        "latitude": lat,
        "longitude": lng,
        "people_count": people,
        "medical_emergency": medical
    }
    try:
        res = requests.post("http://127.0.0.1:8000/send-sos", json=payload, timeout=4)
        if res.status_code == 200:
            st.success("✅ DISTRESS BEACON SENT! NDRF Team Dispatched.")
            st.balloons()
        else:
            st.error("Failed to connect to Rescue Command.")
    except Exception:
        st.error("Rescue Server Offline. Make sure FastAPI is running.")