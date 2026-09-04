# citizen_app.py - Zero-Effort 1-Tap Auto GPS Citizen SOS
import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ResQ-Grid Quick SOS", 
    page_icon="🚨", 
    layout="centered"
)

# High Visibility Emergency Mobile CSS
st.markdown("""
<style>
    .stApp { background-color: #060913; color: #ffffff; }
    
    /* Big Red Pulsing SOS Button */
    .stButton>button {
        background: radial-gradient(circle, #ff003c 0%, #8b0000 100%) !important;
        border: 3px solid #ff4d6d !important;
        color: white !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 0 30px rgba(255, 0, 60, 0.8) !important;
        text-transform: uppercase;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:active {
        transform: scale(0.97);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 ResQ-Grid : 1-Tap SOS")
st.caption("తక్షణ సహాయం కోసం బటన్ నొక్కండి (Instant Emergency Dispatch)")

# 1. Automatic Real-Time GPS Detection using Browser Geolocation
gps_fetcher = """
<script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                // Streamlit URL parameters update to pass coordinates
                const url = new URL(window.parent.location.href);
                if (url.searchParams.get("lat") !== lat.toFixed(5)) {
                    url.searchParams.set("lat", lat.toFixed(5));
                    url.searchParams.set("lng", lng.toFixed(5));
                    window.parent.location.href = url.href;
                }
            }, function(error) {
                console.log("GPS Denied or Error:", error);
            }, {enableHighAccuracy: true});
        }
    }
    getLocation();
</script>
"""
components.html(gps_fetcher, height=0)

# URL లో నుంచి ఆటో-డిటెక్ట్ అయిన GPS రీడ్ చేయడం
query_params = st.query_params
detected_lat = query_params.get("lat", None)
detected_lng = query_params.get("lng", None)

# 2. GPS Status Banner
if detected_lat and detected_lng:
    st.success(f"📍 GPS ఆటోమేటిక్‌గా లాక్ అయ్యింది: `{detected_lat}, {detected_lng}`")
    final_lat = float(detected_lat)
    final_lng = float(detected_lng)
else:
    st.warning("📡 మీ ఫోన్ GPS కోసం చూస్తోంది... స్క్రీన్ పై 'Allow Location' అని వస్తే అనుమతించండి.")
    # Fallback default coordinates (Vijayawada Center)
    final_lat = 16.5062
    final_lng = 80.6480

st.write("---")

# 3. Very Simple Inputs (చదువురాని వాళ్లు కూడా వాడేలా సులభమైన ఫీల్డ్స్)
name = st.text_input("మీ పేరు (Name)", value="Citizen In Need")
people = st.slider("ఎంతమంది చిక్కుకున్నారు? (Trapped Count)", min_value=1, max_value=20, value=3)
medical = st.checkbox("🚑 గాయపడినవారు / అత్యవసర చికిత్స అవసరమా? (Medical Need)", value=True)

st.write("")

# 4. Big Action Button
if st.button("🚨 అత్యవసర సహాయం పంపండి (SEND SOS) 🚨"):
    payload = {
        "user_name": name,
        "latitude": final_lat,
        "longitude": final_lng,
        "people_count": people,
        "medical_emergency": medical
    }
    
    with st.spinner("NDRF కి మీ లోకేషన్ పంపుతున్నాము..."):
        try:
            res = requests.post(
                "https://resqgrid-api.onrender.com/send-sos", 
                json=payload, 
                timeout=30
            )
            if res.status_code == 200:
                st.success("✅ సమాచారం NDRF కమాండ్ సెంటర్‌కు చేరింది! సహాయక బృందం బయలుదేరింది.")
                st.balloons()
            else:
                st.error(f"Error ({res.status_code}): సర్వర్‌కు కనెక్ట్ అవ్వలేదు.")
        except Exception as e:
            st.error(f"నెట్‌వర్క్ సమస్య: {e}")
