# citizen_app.py - High-Accuracy Direct Hardware GPS Citizen SOS
import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

st.set_page_config(
    page_title="ResQ-Grid SOS", 
    page_icon="🚨", 
    layout="centered"
)

# Emergency Styling
st.markdown("""
<style>
    .stApp { background-color: #060913; color: #ffffff; }
    .stButton>button {
        background: radial-gradient(circle, #ff003c 0%, #8b0000 100%) !important;
        border: 3px solid #ff4d6d !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        padding: 18px !important;
        border-radius: 12px !important;
        box-shadow: 0 0 30px rgba(255, 0, 60, 0.8) !important;
        text-transform: uppercase;
        width: 100%;
        margin-top: 10px;
    }
    .gps-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 ResQ-Grid : 1-Tap SOS")
st.caption("ఆపద సమయంలో తక్షణ సహాయం కోసం బటన్ నొక్కండి")

# 1. Reverse Geocoding Helper
@st.cache_data(ttl=300)
def resolve_current_address(lat: float, lon: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "ResQGrid-CitizenLocator"}
    try:
        r = requests.get(url, headers=headers, timeout=5).json()
        addr = r.get("address", {})
        suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("residential") or addr.get("road")
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county")
        state = addr.get("state", "")
        parts = [p for p in [suburb, city, state] if p]
        if parts:
            return ", ".join(parts)
        return r.get("display_name", f"{lat}, {lon}")
    except Exception:
        return f"Sector GPS: {lat:.4f}, {lon:.4f}"

# 2. Direct Mobile Hardware GPS Call
# ఇది ఫోన్ లోని అసలైన సెన్సార్ పర్మిషన్ అడుగుతుంది
loc = get_geolocation()

gps_ready = False
final_lat = 0.0
final_lng = 0.0

if loc and "coords" in loc:
    final_lat = float(loc["coords"]["latitude"])
    final_lng = float(loc["coords"]["longitude"])
    acc = round(loc["coords"].get("accuracy", 5))
    gps_ready = True
    
    place_name = resolve_current_address(final_lat, final_lng)
    
    st.markdown(f"""
    <div class="gps-card">
        <div style="color: #00f0ff; font-weight: bold; font-size: 13px;">📍 లైవ్ లొకేషన్ గుర్తించబడింది (AUTO-LOCKED):</div>
        <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-top: 4px;">{place_name}</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">
            GPS: <code>{final_lat:.5f}, {final_lng:.5f}</code> | ఖచ్చితత్వం: ±{acc} మీటర్లు
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("📡 మీ మొబైల్ GPS కోసం చూస్తోంది... స్క్రీన్ పై **'Allow Location'** అని వస్తే అనుమతించండి.")
    st.caption("చిట్కా: ఫోన్ లో Location ఆన్ ఉన్నా రాకపోతే, బ్రౌజర్ లో పేజీని ఒక్కసారి Refresh చేయండి.")

# 3. Simple Form Inputs
name = st.text_input("మీ పేరు (Name)", value="Citizen In Need")
people = st.slider("ఎంతమంది చిక్కుకున్నారు? (Trapped Count)", min_value=1, max_value=25, value=2)
medical = st.checkbox("🚑 అత్యవసర వైద్య సహాయం అవసరమా? (Urgent Medical)", value=True)

st.write("")

# 4. Big Action Button
if st.button("🚨 అత్యవసర సహాయం పంపండి (SEND SOS) 🚨"):
    if not gps_ready:
        st.error("⚠️ మీ GPS ఇంకా లాక్ అవ్వలేదు. దయచేసి 2 సెకన్లు ఆగి లొకేషన్ పర్మిషన్ ఇవ్వండి.")
    else:
        payload = {
            "user_name": name,
            "latitude": final_lat,
            "longitude": final_lng,
            "people_count": people,
            "medical_emergency": medical
        }
        with st.spinner("NDRF కి మీ ఖచ్చితమైన లొకేషన్ పంపుతున్నాము..."):
            try:
                res = requests.post("https://resqgrid-api.onrender.com/send-sos", json=payload, timeout=35)
                if res.status_code == 200:
                    st.success(f"✅ మీ లొకేషన్ ({place_name}) NDRF వార్-రూమ్‌కు చేరింది!")
                    st.balloons()
                else:
                    st.error(f"సర్వర్ లోపం: {res.status_code}")
            except Exception as e:
                st.error(f"నెట్‌వర్క్ సమస్య: {e}")
