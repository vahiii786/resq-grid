import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & METADATA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ResQ-Grid | Cyber Threat & Rescue War-Room",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CYBER SECURITY HUD THEME (INJECTED CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* Base Dark Background with Cyber Mesh Grid */
.stApp {
    background-color: #040914;
    background-image: 
        linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px);
    background-size: 30px 30px;
    color: #e2e8f0;
    font-family: 'Consolas', 'Courier New', monospace;
}

/* Cyber Headers with Cyan Glow */
h1, h2, h3 {
    color: #00f0ff !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #060d1b !important;
    border-right: 1px solid rgba(0, 240, 255, 0.2);
}

/* Metrics - Glowing Glassmorphic HUD Cards */
div[data-testid="stMetric"] {
    background: rgba(10, 22, 40, 0.75) !important;
    border: 1px solid rgba(0, 240, 255, 0.4) !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    border-radius: 6px;
    padding: 12px;
}
div[data-testid="stMetricLabel"] {
    color: #38bdf8 !important;
    font-size: 12px !important;
    font-weight: bold;
    letter-spacing: 1px;
}
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 26px !important;
    text-shadow: 0 0 8px #00f0ff;
}

/* Interactive Folium Map Frame */
div[data-testid="stCustomComponentV1"] {
    border: 1px solid #00f0ff !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.25) !important;
    border-radius: 8px;
    overflow: hidden;
}

/* Cyber Buttons (Locate on Radar) */
.stButton > button {
    background: rgba(4, 9, 20, 0.8) !important;
    color: #00f0ff !important;
    border: 1px solid #00f0ff !important;
    border-radius: 4px;
    font-weight: bold;
    letter-spacing: 1px;
    transition: all 0.3s ease;
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
}
.stButton > button:hover {
    background: #00f0ff !important;
    color: #040914 !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.8) !important;
}

/* Tactical Alert Cards in Queue */
.triage-card {
    background: rgba(10, 22, 40, 0.65);
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-left: 4px solid #00f0ff;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 12px;
}
.triage-card-critical {
    background: rgba(255, 0, 60, 0.12);
    border: 1px solid rgba(255, 0, 60, 0.5);
    border-left: 4px solid #ff003c;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. BACKEND API CONFIGURATION & SESSION STATE
# -----------------------------------------------------------------------------
# మీ అసలైన Render API URL ఇక్కడ ఇవ్వండి (లేదా లోకల్ టెస్టింగ్ కోసం http://127.0.0.1:8000)
API_BASE_URL = "http://127.0.0.1:8000"

if "map_center" not in st.session_state:
    st.session_state.map_center = [16.5062, 80.6480]  # Default: Vijayawada
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = 13
if "selected_beacon_id" not in st.session_state:
    st.session_state.selected_beacon_id = None
if "last_alert_count" not in st.session_state:
    st.session_state.last_alert_count = 0

# -----------------------------------------------------------------------------
# 4. SIDEBAR - SECTOR CONTROL & THREAT TELEMETRY
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛰️ COMMAND SECTOR")
    st.caption("TACTICAL INCIDENT MANAGEMENT SYSTEM")

    sector_name = st.selectbox(
        "ACTIVE DISASTER ZONE",
        ["Vijayawada (Krishna River)", "Hyderabad (Musi River)", "Rajahmundry (Godavari River)", "Custom Coordinate"]
    )

    if sector_name == "Vijayawada (Krishna River)":
        default_coords = [16.5062, 80.6480]
    elif sector_name == "Hyderabad (Musi River)":
        default_coords = [17.3850, 78.4867]
    elif sector_name == "Rajahmundry (Godavari River)":
        default_coords = [17.0005, 81.8040]
    else:
        default_coords = [16.5062, 80.6480]

    if st.button("RESET TO SECTOR BASE"):
        st.session_state.map_center = default_coords
        st.session_state.map_zoom = 13
        st.session_state.selected_beacon_id = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📡 SATELLITE TELEMETRY")
    st.info("🌧️ **24h Rainfall Total:** 142.4 mm\n\n🚨 **AI Hazard Tier:** CRITICAL RISK")

# -----------------------------------------------------------------------------
# 5. DATA INGESTION ENGINE
# -----------------------------------------------------------------------------
def fetch_active_beacons():
    try:
        res = requests.get(f"{API_BASE_URL}/alerts", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    # బ్యాకెండ్ రన్ అవ్వకపోతే టెస్ట్ చేయడానికి ఫాల్‌బ్యాక్ డెమో డేటా
    return [
        {
            "id": "SOS-101",
            "lat": 16.5120,
            "lon": 80.6400,
            "address": "Gandhi Nagar, Main Road, Vijayawada",
            "people_count": 4,
            "medical": True,
            "timestamp": "18:20:15"
        },
        {
            "id": "SOS-102",
            "lat": 16.5020,
            "lon": 80.6550,
            "address": "Bhavanipuram Lowland Colony, Vijayawada",
            "people_count": 2,
            "medical": False,
            "timestamp": "18:22:40"
        }
    ]

alerts = fetch_active_beacons()

# ఆటోమేటిక్ టోస్ట్ అలర్ట్
if len(alerts) > st.session_state.last_alert_count:
    st.toast(f"🚨 INCOMING DISTRESS BEACON: {len(alerts) - st.session_state.last_alert_count} New Target(s) Locked!", icon="⚡")
    st.session_state.last_alert_count = len(alerts)

# -----------------------------------------------------------------------------
# 6. TOP HUD KPI METRICS
# -----------------------------------------------------------------------------
st.title("🛡️ RESQ-GRID // COMMAND RADAR")
st.caption("INTEGRATED CYBER-PHYSICAL CRISIS SURVEILLANCE MATRIX")

col1, col2, col3, col4 = st.columns(4)
total_civilians = sum(a.get("people_count", 1) for a in alerts)
medical_count = sum(1 for a in alerts if a.get("medical"))

with col1:
    st.metric(label="ACTIVE SOS BEACONS", value=f"{len(alerts)}")
with col2:
    st.metric(label="TRAPPED CIVILIANS", value=f"{total_civilians}")
with col3:
    st.metric(label="MEDICAL CASUALTIES", value=f"{medical_count}")
with col4:
    st.metric(label="SATELLITE SYNC", value="ONLINE (0.02s)")

st.write("")

# -----------------------------------------------------------------------------
# 7. MAIN TACTICAL CONSOLE (MAP & ZERO-FLICKER INCIDENT QUEUE)
# -----------------------------------------------------------------------------
map_col, queue_col = st.columns([7, 3])

with map_col:
    # సైబర్ సెక్యూరిటీ డార్క్ థీమ్ మ్యాప్ (CartoDB Dark Matter)
    f_map = folium.Map(
        location=st.session_state.map_center,
        zoom_start=st.session_state.map_zoom,
        tiles="CartoDB dark_matter"
    )

    for item in alerts:
        is_med = item.get("medical", False)
        is_selected = (item["id"] == st.session_state.selected_beacon_id)

        color = "#ff003c" if is_med else "#00f0ff"
        radius = 12 if is_selected else 8

        # Targeted Victim Circle Marker
        folium.CircleMarker(
            location=[item["lat"], item["lon"]],
            radius=radius,
            color=color,
            weight=3 if is_selected else 1,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            tooltip=f"{item['id']} | {item.get('address', 'Location Locked')}"
        ).add_to(f_map)

        # High-Alert Glowing Ring for Selected Targets
        if is_selected:
            folium.CircleMarker(
                location=[item["lat"], item["lon"]],
                radius=25,
                color="#00f0ff",
                weight=2,
                fill=False
            ).add_to(f_map)

    st_folium(f_map, width="100%", height=550, returned_objects=[])

with queue_col:
    st.subheader("⚠️ LIVE INCIDENT QUEUE")

    # Scoped Fragment: మ్యాప్ రీలోడ్ కాకుండా బ్యాక్‌గ్రౌండ్‌లో ప్రతి 2 సెకన్లకి క్యూ మాత్రమే సింక్ అవుతుంది
    @st.fragment(run_every=2)
    def render_tactical_queue():
        live_alerts = fetch_active_beacons()
        if not live_alerts:
            st.success("NO ACTIVE DISTRESS SIGNALS // SECTOR ALL CLEAR")
            return

        for alert in live_alerts:
            is_critical = alert.get("medical", False)
            card_class = "triage-card-critical" if is_critical else "triage-card"
            badge = "🚨 MEDICAL PRIORITY" if is_critical else "⚡ EVACUATION NEEDED"

            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:bold; color:#00f0ff;">{alert['id']}</span>
                    <span style="font-size:11px; color:#ff003c; font-weight:bold;">{badge}</span>
                </div>
                <div style="font-size:13px; color:#ffffff; margin: 4px 0;">📍 {alert.get('address', 'Exact GPS Locked')}</div>
                <div style="font-size:12px; color:#94a3b8;">
                    👥 Trapped: <b>{alert.get('people_count', 1)}</b> | ⏱️ {alert.get('timestamp', 'Recent')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Targeted Street-Level Camera Lock (Zoom 17)
            if st.button(f"🎯 LOCATE {alert['id']}", key=f"btn_{alert['id']}"):
                st.session_state.map_center = [alert["lat"], alert["lon"]]
                st.session_state.map_zoom = 17
                st.session_state.selected_beacon_id = alert["id"]
                st.rerun()

    render_tactical_queue()
