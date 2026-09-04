# citizen_app.py - High-Precision Auto GPS & Real Address Detection
import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ResQ-Grid SOS", 
    page_icon="🚨", 
    layout="centered"
)

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

# High-Precision Browser Geolocation
gps_component = """
<script>
    const options = { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 };

    function success(pos) {
        const lat = pos.coords.latitude.toFixed(6);
        const lng = pos.coords.longitude.toFixed(6);
        const acc = Math.round(pos.coords.accuracy);

        const url = new URL(window.parent.location.href);
        if (url.searchParams.get("lat") !== lat || url.searchParams.get("lng") !== lng) {
            url.searchParams.set("lat", lat);
            url.searchParams.set("lng", lng);
            url.searchParams.set("acc", acc);
            window.parent.location.href = url.href;
        }
    }
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, function(err){}, options);
    }
</script>
"""
components.html(gps_component, height=0)

# URL Parameters నుండి కోఆర్డినేట్స్ తీసుకోవడం
query_params = st.query_params
detected_lat = query_params.get("lat", None)
detected_lng = query_params.get("lng", None)
detected_acc = query_params.get("acc", None)

@st.cache_data(ttl=300)
def resolve_current_address(lat: float, lon: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "ResQGrid-CitizenLocator"}
    try:
        r = requests.get(url, headers=headers, timeout=4).json()
        addr = r.get("address", {})
        road = addr.get("road") or addr.get("suburb") or addr.get("neighbourhood")
        city = addr.get("city") or addr.get("town") or addr.get("village")
        state = addr.get("state", "")
        parts = [p for p in [road, city, state] if p]
        if parts:
            return ", ".join(parts)
        return r.get("display_name", f"{lat}, {lon}")
    except Exception:
        return f"Sector GPS: {lat}, {lon}"

if detected_lat and detected_lng:
    final_lat = float(detected_lat)
    final_lng = float(detected_lng)
    detected_address = resolve_current_address(final_lat, final_lng)
    
    st.markdown(f"""
    <div class="gps-card">
        <div style="color: #00f0ff; font-weight: bold; font-size: 13px;">📍 మీ ప్రస్తుత లొకేషన్ (AUTO-DETECTED):</div>
        <div style="font-size: 17px; font-weight: 800; color: #ffffff; margin-top: 4px;">{detected_address}</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">
            GPS: <code>{final_lat:.5f}, {final_lng:.5f}</code> (ఖచ్చితత్వం: ±{detected_acc if detected_acc else '5'} మీటర్లు)
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("📡 ఫోన్ నుండి ఖచ్చితమైన GPS తీసుకుంటున్నాము... దయచేసి 'Allow' నొక్కండి.")
    final_lat = 16.5062
    final_lng = 80.6480

name = st.text_input("మీ పేరు (Name)", value="Citizen In Need")
people = st.slider("ఎంతమంది చిక్కుకున్నారు? (Trapped Civilians)", min_value=1, max_value=25, value=2)
medical = st.checkbox("🚑 అత్యవసర వైద్య సహాయం అవసరమా? (Urgent Medical)", value=True)

st.write("")
if st.button("🚨 అత్యవసర సహాయం పంపండి (SEND SOS) 🚨"):
    payload = {
        "user_name": name,
        "latitude": final_lat,
        "longitude": final_lng,
        "people_count": people,
        "medical_emergency": medical
    }
    with st.spinner("NDRF కి మీ లొకేషన్ వివరాలు పంపుతున్నాము..."):
        try:
            res = requests.post("https://resqgrid-api.onrender.com/send-sos", json=payload, timeout=35)
            if res.status_code == 200:
                st.success("✅ మీ వివరాలు NDRF వార్-రూమ్ కమాండ్ సెంటర్‌కు చేరాయి!")
                st.balloons()
            else:
                st.error(f"సర్వర్ లోపం: {res.status_code}")
        except Exception as e:
            st.error(f"కనెక్షన్ సమస్య: {e}")
