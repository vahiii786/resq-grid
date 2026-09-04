# citizen_app.py - High-Precision Pinpoint GPS Citizen SOS
import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ResQ-Grid Pinpoint SOS", 
    page_icon="🚨", 
    layout="centered"
)

# High Visibility Emergency Mobile CSS
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
    .stButton>button:active {
        transform: scale(0.97);
    }
    .gps-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 ResQ-Grid : 1-Tap SOS")
st.caption("తక్షణ సహాయం కోసం బటన్ నొక్కండి (Instant Emergency Dispatch)")

# High Precision HTML5 Geolocation Component
# enableHighAccuracy: true ఫోన్ లోపల ఉన్న శాటిలైట్ GPS చిప్‌ను ఆన్ చేసి exact మీటర్లలో పిన్ పాయింట్ చేస్తుంది.
gps_component = """
<div id="gps-status" style="color: #94a3b8; font-family: sans-serif; font-size: 13px; text-align: center; padding: 6px;">
    🛰️ శాటిలైట్ GPS లాక్ అవుతోంది...
</div>

<script>
    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
    };

    function success(pos) {
        const crd = pos.coords;
        const lat = crd.latitude.toFixed(6);
        const lng = crd.longitude.toFixed(6);
        const acc = Math.round(crd.accuracy);
        
        document.getElementById("gps-status").innerHTML = 
            `<b style="color:#00f0ff;">✓ ఖచ్చితమైన GPS లాక్ అయ్యింది:</b> ${lat}, ${lng} (Accuracy: ±${acc}m)`;

        const url = new URL(window.parent.location.href);
        if (url.searchParams.get("lat") !== lat || url.searchParams.get("lng") !== lng) {
            url.searchParams.set("lat", lat);
            url.searchParams.set("lng", lng);
            url.searchParams.set("acc", acc);
            window.parent.location.href = url.href;
        }
    }

    function error(err) {
        document.getElementById("gps-status").innerHTML = 
            `<span style="color:#ff003c;">⚠️ GPS యాక్సెస్ లభించలేదు. దయచేసి మొబైల్ లో Location ఆన్ చేయండి.</span>`;
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error, options);
    }
</script>
"""

components.html(gps_component, height=55)

# Read coordinates from URL Query Parameters
query_params = st.query_params
detected_lat = query_params.get("lat", None)
detected_lng = query_params.get("lng", None)
detected_acc = query_params.get("acc", None)

if detected_lat and detected_lng:
    st.markdown(f"""
    <div class="gps-box">
        <div style="color: #00f0ff; font-weight: bold; font-size: 14px;">📍 LIVE PINPOINT COORDINATES</div>
        <div style="font-size: 16px; font-weight: bold; margin-top: 4px;">Lat: {detected_lat} | Lng: {detected_lng}</div>
        <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">GPS Accuracy: ఖచ్చితత్వం ±{detected_acc if detected_acc else '5'} మీటర్లు</div>
    </div>
    """, unsafe_allow_html=True)
    final_lat = float(detected_lat)
    final_lng = float(detected_lng)
else:
    st.warning("⚠️ ఖచ్చితమైన లొకేషన్ కోసం ఫోన్ లో 'Location' (GPS) ఆన్ చేసి, బ్రౌజర్ లో 'Allow' క్లిక్ చేయండి.")
    final_lat = 16.5062
    final_lng = 80.6480

# 3. Simple Form Inputs
name = st.text_input("మీ పేరు (Name)", value="Citizen In Need")
people = st.slider("ఎంతమంది చిక్కుకున్నారు? (Trapped Count)", min_value=1, max_value=20, value=3)
medical = st.checkbox("🚑 గాయపడినవారు / అత్యవసర చికిత్స అవసరమా? (Medical Need)", value=True)

st.write("")

# 4. Action Button
if st.button("🚨 అత్యవసర సహాయం పంపండి (SEND SOS) 🚨"):
    payload = {
        "user_name": name,
        "latitude": final_lat,
        "longitude": final_lng,
        "people_count": people,
        "medical_emergency": medical
    }
    
    with st.spinner("NDRF కి మీ ఖచ్చితమైన లొకేషన్ పంపుతున్నాము..."):
        try:
            res = requests.post(
                "https://resqgrid-api.onrender.com/send-sos", 
                json=payload, 
                timeout=35
            )
            if res.status_code == 200:
                st.success("✅ ఖచ్చితమైన లొకేషన్ NDRF కమాండ్ సెంటర్‌కు చేరింది! రెస్క్యూ బృందం బయలుదేరింది.")
                st.balloons()
            else:
                st.error(f"సర్వర్ లోపం ({res.status_code})")
        except Exception as e:
            st.error(f"నెట్‌వర్క్ సమస్య: {e}")
