# citizen_app.py - ResQ-Grid Citizen SOS (Dynamic Offline SMS & GPS Integration)
import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

st.set_page_config(
    page_title="ResQ-Grid Citizen SOS",
    page_icon="🚨",
    layout="centered"
)

API_BASE_URL = "https://resqgrid-api.onrender.com"

st.markdown("""
<style>
    .stApp {
        background-color: #030712;
        color: #f1f5f9;
        font-family: sans-serif;
    }
    .offline-box {
        background: rgba(255, 0, 85, 0.15);
        border: 1px solid #ff0055;
        border-radius: 8px;
        padding: 16px;
        margin-top: 18px;
        text-align: center;
    }
    .sms-btn {
        display: inline-block;
        width: 100%;
        background: linear-gradient(90deg, #d90429 0%, #8d0801 100%);
        color: #ffffff !important;
        font-weight: bold;
        text-decoration: none;
        padding: 14px 20px;
        border-radius: 6px;
        border: 1px solid #ff0055;
        box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
        text-align: center;
        margin-top: 12px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 RESQ-GRID // CITIZEN SOS")
st.caption("EMERGENCY DISTRESS BEACON — TRIBAL & URBAN LIFELINE")

# Hardware GPS Detection
loc = get_geolocation()
lat, lng, acc = 0.0, 0.0, 0.0

if loc and "coords" in loc:
    lat = loc["coords"]["latitude"]
    lng = loc["coords"]["longitude"]
    acc = loc["coords"].get("accuracy", 10.0)
    st.success(f"📍 GPS LOCKED: `{lat:.5f}, {lng:.5f}` (±{acc:.1f}m accuracy)")
else:
    st.warning("⚠️ Accessing Satellite GPS... Allow location permission on your device.")

st.write("")

# Triage Inputs
user_name = st.text_input("Your Name / Hamlet Name (గ్రామం పేరు)", value="Citizen")
people = st.slider("Total People Trapped (రక్షించాల్సిన వ్యక్తుల సంఖ్య)", 1, 25, 4)
is_medical = st.checkbox("🚨 Critical Medical Emergency / Urgent Trauma (అత్యవసర వైద్యం అవసరం)")

st.write("---")

# Mode A: Online Internet Transmission
if st.button("⚡ TRANSMIT SOS VIA CLOUD (ఇంటర్నెట్ ఉన్నప్పుడు)", use_container_width=True):
    if lat == 0.0 and lng == 0.0:
        st.error("GPS coordinates not acquired yet. Please wait for satellite fix.")
    else:
        payload = {
            "user_name": user_name,
            "latitude": lat,
            "longitude": lng,
            "people_count": people,
            "medical_emergency": is_medical
        }
        try:
            res = requests.post(f"{API_BASE_URL}/send-sos", json=payload, timeout=5)
            if res.status_code in [200, 201]:
                st.success("✅ SOS BEACON TRANSMITTED TO COMMAND CENTER RADAR!")
                st.balloons()
            else:
                st.error("Server error. Please use Offline SMS below.")
        except Exception:
            st.error("❌ Cloud Network Failed (No Internet). Use Offline SMS below immediately!")

# Mode B: Zero-Network Offline SMS Fallback (Custom Dynamic Number)
st.markdown("### 📶 OFFLINE SMS DISPATCH")
target_phone = st.text_input("Helpline / Dispatcher Phone Number (SMS పంపాల్సిన నంబర్)", value="+91112")

sms_body = f"SOS#RESQGRID#LOC:{lat:.5f},{lng:.5f}#NAME:{user_name}#P:{people}#MED:{1 if is_medical else 0}#TO:{target_phone}"
sms_uri = f"sms:{target_phone}?body={sms_body}"

st.markdown(f"""
<div class="offline-box">
    <div style="font-weight: bold; font-size: 15px; color: #ff0055;">
        ZERO-INTERNET / TRIBAL EMERGENCY FALLBACK
    </div>
    <div style="font-size: 13px; color: #cbd5e1; margin-top: 5px;">
        డేటా నెట్‌వర్క్ లేనప్పుడు, ఈ బటన్ క్లిక్ చేస్తే <code>{target_phone}</code> కు డైరెక్ట్ SMS ద్వారా GPS లొకేషన్ వెళ్తుంది.
    </div>
    <a class="sms-btn" href="{sms_uri}">
        📩 SEND OFFLINE SOS TO {target_phone}
    </a>
</div>
""", unsafe_allow_html=True)
