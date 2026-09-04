# citizen_app.py - Citizen Mobile SOS Interface
import streamlit as st
import requests

st.set_page_config(page_title="ResQ-Grid Citizen SOS", page_icon="🚨", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #fff; }
    .stButton>button {
        background: radial-gradient(circle, #ff003c 0%, #990000 100%) !important;
        border: 2px solid #ff4d6d !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        padding: 15px !important;
        box-shadow: 0 0 25px rgba(255, 0, 60, 0.7);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 ResQ-Grid SOS")
st.caption("Citizen Emergency Distress Transmitter")

name = st.text_input("Your Name / మీ పేరు", value="Ramesh Kumar")
people = st.number_input("Number of People Trapped / చిక్కుకున్న వారి సంఖ్య", min_value=1, max_value=50, value=3)
medical = st.checkbox("🚑 Urgent Medical Assistance Needed (గాయపడినవారు ఉన్నారు)", value=True)

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
    
    with st.spinner("Connecting to NDRF Satellite Uplink (Render Cloud)..."):
        try:
            # Timeout 40 seconds to handle Render cold-start
            res = requests.post("https://resqgrid-api.onrender.com/send-sos", json=payload, timeout=40)
            if res.status_code == 200:
                st.success("✅ DISTRESS BEACON SENT! NDRF Team Dispatched.")
                st.balloons()
            else:
                st.error(f"Server Error ({res.status_code}): {res.text}")
        except requests.exceptions.Timeout:
            st.error("⏳ Server waking up from sleep. Please tap SOS button once again!")
        except Exception as e:
            st.error(f"⚠️ Connection Issue: {e}")
