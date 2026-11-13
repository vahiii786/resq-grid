# dashboard.py - ResQ-Grid Command Interface (Cyber Shield Theme + Full SMS Gateway & Agency Watch)
import streamlit as st
import folium
import requests
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ResQ-Grid | Disaster Management System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "https://resqgrid-api.onrender.com"

# Pre-mapped Tribal Agency Sectors
TRIBAL_ZONES = {
    "Rampachodavaram Agency (Alluri District)": {"lat": 17.4475, "lng": 81.7774, "danger_threshold": 100.0},
    "Araku Valley Agency (Visakhapatnam)": {"lat": 18.3273, "lng": 82.8775, "danger_threshold": 95.0},
    "Bhadrachalam Agency (Godavari Basin)": {"lat": 17.6688, "lng": 80.8936, "danger_threshold": 110.0}
}

# Session State Persistence
if "focused_coords" not in st.session_state:
    st.session_state["focused_coords"] = None
if "focused_user" not in st.session_state:
    st.session_state["focused_user"] = None
if "last_search" not in st.session_state:
    st.session_state["last_search"] = "Vijayawada"
if "prev_alert_count" not in st.session_state:
    st.session_state["prev_alert_count"] = 0

# Cyber Shield Defense UI Styling (Sidebar Contrast Bug Fixed)
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">

<style>
    * { font-family: 'Rajdhani', sans-serif !important; }
    code, pre, .mono-text { font-family: 'Share Tech Mono', monospace !important; }
    
    .stApp {
        background-color: #030712;
        background-image: 
            linear-gradient(to right, rgba(0, 212, 255, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 212, 255, 0.04) 1px, transparent 1px),
            radial-gradient(circle at 10% 20%, rgba(0, 212, 255, 0.18), transparent 45%),
            radial-gradient(circle at 90% 40%, rgba(255, 0, 85, 0.16), transparent 50%),
            radial-gradient(circle at 50% 100%, rgba(15, 23, 42, 0.9), transparent 70%);
        background-size: 32px 32px, 32px 32px, 100% 100%, 100% 100%, 100% 100%;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    @keyframes radarPulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.8); }
        70% { box-shadow: 0 0 0 14px rgba(255, 0, 85, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
    }

    .hud-panel {
        background: rgba(8, 14, 30, 0.82);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 8px;
        padding: 16px 20px;
        position: relative;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.85);
    }
    
    .hud-panel::before {
        content: ""; position: absolute; top: 0; left: 0; width: 12px; height: 12px;
        border-top: 2px solid #00d4ff; border-left: 2px solid #00d4ff;
    }
    .hud-panel::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 12px; height: 12px;
        border-bottom: 2px solid #ff0055; border-right: 2px solid #ff0055;
    }

    .kpi-container {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        background: rgba(11, 20, 42, 0.8);
        border-top: 2px solid #00d4ff; 
        border-bottom: 1px solid rgba(0, 212, 255, 0.15);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        padding: 14px; border-radius: 6px;
    }
    .kpi-title { font-family: 'Share Tech Mono', monospace !important; font-size: 11px; color: #38bdf8; letter-spacing: 2px; }
    .kpi-num { font-size: 32px; font-weight: 800; margin-top: 2px; text-shadow: 0 0 12px currentColor; }

    .pulse-dot {
        height: 10px; width: 10px; background-color: #ff0055;
        border-radius: 50%; display: inline-block; animation: radarPulse 2s infinite; margin-right: 8px;
    }

    /* Sidebar Base Styling */
    [data-testid="stSidebar"] {
        background: #040817 !important;
        border-right: 1px solid rgba(0, 212, 255, 0.35) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.8);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #ffffff !important; font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small, [data-testid="stSidebar"] .mono-text {
        color: #00d4ff !important; font-weight: bold !important;
    }
    [data-testid="stSidebar"] input {
        background-color: #09132b !important; color: #ffffff !important;
        border: 1px solid #00d4ff !important; font-weight: 700 !important;
        box-shadow: inset 0 0 8px rgba(0, 212, 255, 0.2);
    }

    /* FIX: Force Dark Background on Sidebar Alerts (Success, Warning, Info, Error) */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(9, 19, 43, 0.95) !important;
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 4px rgba(255, 255, 255, 0.2);
    }
    [data-testid="stSidebar"] [data-testid="stAlert"][kind="error"] {
        border-color: #ff0055 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"][kind="warning"] {
        border-color: #f59e0b !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"][kind="success"] {
        border-color: #10b981 !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #d90429 0%, #8d0801 100%) !important;
        color: #ffffff !important; 
        border: 1px solid #ff0055 !important;
        font-weight: 700 !important; 
        letter-spacing: 1.5px !important;
        text-transform: uppercase; 
        border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(255, 0, 85, 0.35);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ef233c 0%, #b80c09 100%) !important;
        box-shadow: 0 0 25px rgba(255, 0, 85, 0.75); 
        transform: translateY(-1px);
    }

    iframe {
        display: block;
        width: 100% !important;
        border-radius: 8px; 
        border: 1px solid rgba(0, 212, 255, 0.4) !important;
        filter: invert(93%) hue-rotate(180deg) brightness(95%) contrast(90%);
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_data(ttl=3600)
def get_coordinates(query: str):
    url = f"https://nominatim.openstreetmap.org/search?q={query},India&format=json&limit=1"
    headers = {"User-Agent": "ResQGrid-TacticalEngine"}
    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        if res:
            return {
                "name": res[0]["display_name"].split(",")[0],
                "lat": float(res[0]["lat"]),
                "lng": float(res[0]["lon"])
            }
    except Exception:
        pass
    return {"name": "Vijayawada", "lat": 16.5062, "lng": 80.6480}

@st.cache_data(ttl=600)
def get_place_name(lat: float, lon: float) -> str:
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {"User-Agent": "ResQGrid-TacticalEngine"}
    try:
        res = requests.get(url, headers=headers, timeout=4).json()
        address = res.get("address", {})
        suburb = address.get("suburb") or address.get("neighbourhood") or address.get("residential") or address.get("road")
        city = address.get("city") or address.get("town") or address.get("village") or address.get("county")
        if suburb and city:
            return f"{suburb}, {city}"
        elif city:
            return city
        elif res.get("display_name"):
            return ", ".join(res.get("display_name").split(",")[:2])
    except Exception:
        pass
    return f"Sector ({lat:.3f}, {lon:.3f})"

def fetch_satellite_rain(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=rain&timezone=auto"
    try:
        res = requests.get(url, timeout=5).json()
        hourly_rain = res.get("hourly", {}).get("rain", [])
        total_rain = sum(hourly_rain[:24]) if hourly_rain else 0.0
        return round(float(total_rain), 2)
    except Exception:
        return 0.0

# Fetch Active SOS Signals
sos_list = []
try:
    sos_res = requests.get(f"{API_BASE_URL}/all-sos", timeout=4).json()
    sos_list = sos_res.get("active_emergencies", [])
except Exception:
    pass

# Header Section
st.markdown("""
<div class="hud-panel" style="margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="display:flex; align-items:center;">
                <span class="pulse-dot"></span>
                <span style="font-family: 'Share Tech Mono', monospace; color: #ff0055; font-size: 12px; letter-spacing: 2px;">TACTICAL DISASTER DEFENSE MATRIX ACTIVE</span>
            </div>
            <h1 style="margin: 2px 0 0 0; font-size: 28px; font-weight: 800; letter-spacing: 1px; color: #f8fafc; text-shadow: 0 0 15px rgba(0, 212, 255, 0.4);">
                RESQ-GRID <span style="color: #00d4ff;">COMMAND SYSTEM</span>
            </h1>
            <p style="margin: 0; color: #64748b; font-size: 13px;" class="mono-text">
                NDRF Integrated Early Warning Flood Detection & Automated Tribal Surveillance
            </p>
        </div>
        <div style="text-align: right;" class="mono-text">
            <span style="color: #00d4ff; font-weight: bold; font-size: 14px; text-shadow: 0 0 10px #00d4ff;">[ SHIELD ENGAGED ]</span><br>
            <span style="color: #94a3b8; font-size: 11px;">Agency Link: STANDBY</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metrics Row
k1, k2, k3, k4 = st.columns(4)
total_trapped = sum(item.get("people", 0) for item in sos_list)
critical_cases = sum(1 for item in sos_list if item.get("medical_urgent", False))

with k1:
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">TOTAL SOS ALERTS</div><div class="kpi-num" style="color: #ff0055;">{len(sos_list):02d}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #f59e0b;"><div class="kpi-title">PEOPLE TRAPPED</div><div class="kpi-num" style="color: #f59e0b;">{total_trapped:02d}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #ec4899;"><div class="kpi-title">MEDICAL EMERGENCIES</div><div class="kpi-num" style="color: #ec4899;">{critical_cases:02d}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-container" style="border-top-color: #00d4ff;"><div class="kpi-title">RADAR STATUS</div><div class="kpi-num" style="color: #00d4ff;">ACTIVE</div></div>', unsafe_allow_html=True)

st.write("")

# Sidebar Controls
st.sidebar.markdown("### 📍 SELECT LOCATION")
search_area = st.sidebar.text_input("Search City / Town", value=st.session_state["last_search"])

if search_area != st.session_state["last_search"]:
    st.session_state["last_search"] = search_area
    st.session_state["focused_coords"] = None
    st.session_state["focused_user"] = None

target = get_coordinates(search_area)
st.sidebar.caption(f"Area: `{target['name']}` | GPS: `{target['lat']:.4f}, {target['lng']:.4f}`")
st.sidebar.markdown("---")

st.sidebar.markdown("### ⚙️ WEATHER DATA SOURCE")
data_mode = st.sidebar.radio(
    "Choose Mode",
    ["🛰️ Automatic (Live Satellite)", "🎛️ Manual (Test Simulation)"]
)

if data_mode == "🛰️ Automatic (Live
