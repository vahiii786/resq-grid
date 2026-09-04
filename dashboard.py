# dashboard.py - ResQ-Grid Command Interface (Smart Auto-Centering Edition)
import streamlit as st
import folium
import requests
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="ResQ-Grid | Disaster Management System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Centralized Cloud Backend URL
API_BASE_URL = "https://resqgrid-api.onrender.com"

# 2. High-Tech Styling + Clear Visual Contrast
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">

<style>
    * {
        font-family: 'Rajdhani', sans-serif !important;
    }
    code, pre, .mono-text {
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    .stApp {
        background-color: #030712;
        background-image: 
            linear-gradient(to right, rgba(0, 240, 255, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 240, 255, 0.05) 1px, transparent 1px),
            radial-gradient(circle at 50% 0%, rgba(255, 0, 60, 0.15), transparent 60%),
            radial-gradient(circle at 100% 100%, rgba(0, 110, 255, 0.12), transparent 50%);
        background-size: 35px 35px, 35px 35px, 100% 100%, 100% 100%;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    @keyframes radarPulse {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    .hud-panel {
        background: rgba(10, 15, 29, 0.85);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-radius: 8px;
        padding: 16px 20px;
        position: relative;
        box-shadow: 0 8px 30px rgba(0,0,0,0.7);
    }
    
    .hud-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 10px; height: 10px;
        border-top: 2px solid #00f0ff;
        border-left: 2px solid #00f0ff;
    }
    .hud-panel::after {
        content: "";
        position: absolute;
        bottom: 0; right: 0; width: 10px; height: 10px;
        border-bottom: 2px solid #ff003c;
        border-right: 2px solid #ff003c;
    }

    .kpi-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: rgba(15, 23, 42, 0.75);
        border-top: 2px solid #00f0ff;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 14px;
        border-radius: 6px;
    }
    .kpi-title {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 11px;
        color: #94a3b8;
        letter-spacing: 2px;
    }
    .kpi-num {
        font-size: 32px;
        font-weight: 800;
        margin-top: 2px;
    }

    .pulse-dot {
        height: 10px;
        width: 10px;
        background-color: #ef4444;
        border-radius: 50%;
        display: inline-block;
        animation: radarPulse 2s infinite;
        margin-right: 8px;
    }

    /* High Contrast Sidebar */
    [data-testid="stSidebar"] {
        background: #040711 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.3) !important;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stCaption, 
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] .mono-text {
        color: #00f0ff !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] input {
        background-color: #0b1329 !important;
        color: #ffffff !important;
        border: 1px solid #00f0ff !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #b91c1c 0%, #7f1d1d 100%) !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
        border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #dc2626 0%, #991b1b 100%) !important;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.6);
        transform: translateY(-1px);
    }

    iframe {
        border-radius: 8px;
        border: 1px solid rgba(0, 240, 255, 0.25) !important;
        filter: invert(93%) hue-rotate(180deg) brightness(95%) contrast(90%);
    }
</style>
""", unsafe_allow_html=True)

# 3. Helpers: Geocoding & Satellite Weather
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

def fetch_satellite_rain(lat: float, lon: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=rain&timezone=auto"
    try:
        res = requests.get(url, timeout=5).json()
        hourly_rain = res.get("hourly", {}).get("rain", [])
        total_rain = sum(hourly_rain[:24]) if hourly_rain else 0.0
        return round(float(total_rain), 2)
    except Exception:
        return 0.0

# Fetch Live SOS Alerts from Cloud Server
sos_list = []
try:
    sos_res = requests.get(f"{API_BASE_URL}/all-sos", timeout=10).json()
    sos_list = sos_res.get("active_emergencies", [])
except Exception:
    pass

# 4. Top Operations Header
st.markdown("""
<div class="hud-panel" style="margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="display:flex; align-items:center;">
                <span class="pulse-dot"></span>
                <span style="font-family: 'Share Tech Mono', monospace; color: #ef4444; font-size: 12px; letter-spacing: 2px;">LIVE MONITORING ACTIVE</span>
            </div>
            <h1 style="margin: 2px 0 0 0; font-size: 28px; font-weight: 800; letter-spacing: 1px; color: #f8fafc;">
                RESQ-GRID <span style="color: #00f0ff;">COMMAND CENTER</span>
            </h1>
            <p style="margin: 0; color: #64748b; font-size: 13px;" class="mono-text">
                NDRF Early Warning Flood Detection & Real-Time Citizen Rescue System
            </p>
        </div>
        <div style="text-align: right;" class="mono-text">
            <span style="color: #00f0ff; font-weight: bold; font-size: 14px;">[ SYSTEM ONLINE ]</span><br>
            <span style="color: #94a3b8; font-size: 11px;">Cloud Uplink: CONNECTED</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Clear Overview Metrics
k1, k2, k3, k4 = st.columns(4)
total_trapped = sum(item.get("people", 0) for item in sos_list)
critical_cases = sum(1 for item in sos_list if item.get("medical_urgent", False))

with k1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-title">TOTAL SOS ALERTS</div>
        <div class="kpi-num" style="color: #ff003c;">{len(sos_list):02d}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color: #f59e0b;">
        <div class="kpi-title">PEOPLE TRAPPED</div>
        <div class="kpi-num" style="color: #f59e0b;">{total_trapped:02d}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color: #ec4899;">
        <div class="kpi-title">MEDICAL EMERGENCIES</div>
        <div class="kpi-num" style="color: #ec4899;">{critical_cases:02d}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown("""
    <div class="kpi-container" style="border-top-color: #10b981;">
        <div class="kpi-title">RADAR STATUS</div>
        <div class="kpi-num" style="color: #10b981;">ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# 6. Sidebar Controls
st.sidebar.markdown("### 📍 SELECT LOCATION")
search_area = st.sidebar.text_input("Search City / Town", value="Vijayawada")
target = get_coordinates(search_area)

st.sidebar.caption(f"Sector Baseline: `{target['name']}` | `{target['lat']:.4f}, {target['lng']:.4f}`")
st.sidebar.markdown("---")

# Weather Data Selection
st.sidebar.markdown("### ⚙️ WEATHER DATA SOURCE")
data_mode = st.sidebar.radio(
    "Choose Mode",
    ["🛰️ Automatic (Live Satellite)", "🎛️ Manual (Test Simulation)"]
)

if data_mode == "🛰️ Automatic (Live Satellite)":
    live_rain = fetch_satellite_rain(target["lat"], target["lng"])
    st.sidebar.success(f"Live Rain (Past 24h): **{live_rain} mm**")
    rain_val = live_rain
    water_lvl = 6.2
    elev_val = 15.0
    st.sidebar.caption("River Level: Estimated from local sensors (~6.2m)")
else:
    rain_val = st.sidebar.slider("Rainfall (24h in mm)", 0.0, 300.0, 140.0)
    water_lvl = st.sidebar.slider("Flood Water Level (in meters)", 0.0, 15.0, 7.5)
    elev_val = st.sidebar.number_input("Ground Height / Elevation (meters)", value=14.0)

if st.sidebar.button("⚡ CHECK FLOOD RISK (AI)", use_container_width=True):
    payload = {
        "area_name": target["name"],
        "rainfall_mm": rain_val,
        "river_level_m": water_lvl,
        "elevation_m": elev_val
    }
    try:
        r = requests.post(f"{API_BASE_URL}/check-risk", json=payload, timeout=10).json()
        eval_data = r["result"]
        lvl = eval_data["level"]
        score = eval_data["risk_score"]
        
        st.sidebar.markdown("#### 🛡️ AI RISK RESULT")
        if lvl == "CRITICAL":
            st.sidebar.error(f"THREAT LEVEL: {lvl} [Score: {score}]")
        elif lvl == "ALERT":
            st.sidebar.warning(f"THREAT LEVEL: {lvl} [Score: {score}]")
        else:
            st.sidebar.success(f"THREAT LEVEL: {lvl} [Score: {score}]")
        st.sidebar.info(eval_data["action"])
    except Exception:
        st.sidebar.error("Cloud Backend Connection Error.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚨 TEST CITIZEN SOS")
if st.sidebar.button(f"Send Mock SOS in {target['name']}", use_container_width=True):
    mock = {
        "user_name": f"Citizen ({target['name']})",
        "latitude": target["lat"] + 0.003,
        "longitude": target["lng"] + 0.003,
        "people_count": 4,
        "medical_emergency": True
    }
    try:
        requests.post(f"{API_BASE_URL}/send-sos", json=mock, timeout=10)
        st.sidebar.success("SOS Alert Sent to Queue!")
        st.rerun()
    except Exception:
        st.sidebar.error("Could not send SOS alert.")

# 7. Main Split Layout with Smart Auto-Centering Map
col_radar, col_queue = st.columns([7, 4])

with col_radar:
    # Check if SOS beacons exist to center map dynamically on the incident
    if sos_list:
        latest_sos = sos_list[-1]
        map_lat = latest_sos["location"]["lat"]
        map_lng = latest_sos["location"]["lng"]
        map_zoom = 15
        st.markdown(f"#### 🗺️ LIVE INCIDENT RADAR — `FOCUSED ON ACTIVE SOS`", unsafe_allow_html=True)
    else:
        map_lat = target["lat"]
        map_lng = target["lng"]
        map_zoom = 13
        st.markdown(f"#### 🗺️ LIVE FLOOD MAP — `{target['name'].upper()}`", unsafe_allow_html=True)

    radar_map = folium.Map(
        location=[map_lat, map_lng], 
        zoom_start=map_zoom,
        max_zoom=19,
        tiles="OpenStreetMap"
    )

    # Perimeter Circle around focus
    folium.Circle(
        location=[map_lat, map_lng],
        radius=2500,
        color="#ff003c",
        weight=2,
        fill=True,
        fill_color="#ff003c",
        fill_opacity=0.2,
        tooltip="Active Danger Perimeter"
    ).add_to(radar_map)

    # Plot all SOS beacons
    for item in sos_list:
        loc = [item["location"]["lat"], item["location"]["lng"]]
        user = item.get("user", "Unknown")
        count = item.get("people", 1)
        med = item.get("medical_urgent", False)
        
        # High visibility marker
        folium.Marker(
            location=loc,
            tooltip=f"🚨 SOS: {user}",
            popup=f"<b>{user}</b><br>Trapped: {count}<br>Medical Emergency: {med}<br>GPS: {loc[0]:.5f}, {loc[1]:.5f}",
            icon=folium.Icon(color="red" if med else "orange", icon="warning-sign" if med else "user")
        ).add_to(radar_map)
        
        # Glowing radar ring around pin
        folium.CircleMarker(
            location=loc,
            radius=16,
            color="#ff003c",
            weight=3,
            fill=True,
            fill_color="#ff003c",
            fill_opacity=0.45
        ).add_to(radar_map)

    components.html(radar_map._repr_html_(), height=550)

with col_queue:
    st.markdown("#### 🚨 NDRF LIVE RESCUE QUEUE")
    
    if st.button("🔄 REFRESH ALERTS", use_container_width=True):
        st.rerun()
        
    if sos_list:
        for idx, alert in enumerate(reversed(sos_list)):
            urgent_badge = "<span style='color:#ff003c; font-weight:bold;'>[URGENT: MEDICAL HELP NEEDED]</span>" if alert.get("medical_urgent") else "<span style='color:#00f0ff;'>[STANDARD RESCUE]</span>"
            st.markdown(f"""
            <div class="hud-panel" style="margin-bottom: 12px; border-left: 3px solid #ff003c;">
                <div style="font-weight: bold; font-size: 15px; color: #f8fafc;" class="mono-text">
                    ALERT #{len(sos_list)-idx:02d} : {alert.get('user')}
                </div>
                <div style="font-size: 12px; margin: 4px 0;" class="mono-text">{urgent_badge}</div>
                <div style="font-size: 13px; color: #94a3b8;" class="mono-text">
                    People: <b style="color:#f8fafc;">{alert.get('people')}</b> | GPS: <code>{alert['location']['lat']:.5f}, {alert['location']['lng']:.5f}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hud-panel" style="text-align: center; border: 1px dashed rgba(0, 240, 255, 0.3);">
            <p style="color: #00f0ff; margin:0; font-size: 14px; font-weight: 700;" class="mono-text">✓ NO ACTIVE RESCUE REQUESTS</p>
            <p style="color: #64748b; font-size: 12px; margin: 4px 0 0 0;" class="mono-text">All areas are currently normal and safe.</p>
        </div>
        """, unsafe_allow_html=True)
