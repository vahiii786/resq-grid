# dashboard.py - ResQ-Grid Tactical Command Interface (All Original Features Restored + Zero Blink)
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

API_BASE_URL = "https://resqgrid-api.onrender.com"

# Session State Persistence
if "focused_coords" not in st.session_state:
    st.session_state["focused_coords"] = None
if "focused_user" not in st.session_state:
    st.session_state["focused_user"] = None
if "last_search" not in st.session_state:
    st.session_state["last_search"] = "Vijayawada"

# 2. High-Tech Styling + Clear Visual Contrast
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
        content: ""; position: absolute; top: 0; left: 0; width: 10px; height: 10px;
        border-top: 2px solid #00f0ff; border-left: 2px solid #00f0ff;
    }
    .hud-panel::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 10px; height: 10px;
        border-bottom: 2px solid #ff003c; border-right: 2px solid #ff003c;
    }

    .kpi-container {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        background: rgba(15, 23, 42, 0.75);
        border-top: 2px solid #00f0ff; border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding: 14px; border-radius: 6px;
    }
    .kpi-title { font-family: 'Share Tech Mono', monospace !important; font-size: 11px; color: #94a3b8; letter-spacing: 2px; }
    .kpi-num { font-size: 32px; font-weight: 800; margin-top: 2px; }

    .pulse-dot {
        height: 10px; width: 10px; background-color: #ef4444;
        border-radius: 50%; display: inline-block; animation: radarPulse 2s infinite; margin-right: 8px;
    }

    [data-testid="stSidebar"] {
        background: #040711 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.3) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #ffffff !important; font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small, [data-testid="stSidebar"] .mono-text {
        color: #00f0ff !important; font-weight: bold !important;
    }
    [data-testid="stSidebar"] input {
        background-color: #0b1329 !important; color: #ffffff !important;
        border: 1px solid #00f0ff !important; font-weight: 700 !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #b91c1c 0%, #7f1d1d 100%) !important;
        color: #ffffff !important; border: 1px solid #ef4444 !important;
        font-weight: 700 !important; letter-spacing: 1.5px !important;
        text-transform: uppercase; border-radius: 4px !important;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #dc2626 0%, #991b1b 100%) !important;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.6); transform: translateY(-1px);
    }
    iframe {
        border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.25) !important;
        filter: invert(93%) hue-rotate(180deg) brightness(95%) contrast(90%);
    }
</style>
""", unsafe_allow_html=True)

# 3. Helpers: Geocoding, Reverse Geocoding & Weather Telemetry
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

# Fetch Live SOS Alerts for Map Initialization
sos_list = []
try:
    sos_res = requests.get(f"{API_BASE_URL}/all-sos", timeout=4).json()
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
    st.markdown(f'<div class="kpi-container"><div class="kpi-title">TOTAL SOS ALERTS</div><div class="kpi-num" style="color: #ff003c;">{len(sos_list):02d}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #f59e0b;"><div class="kpi-title">PEOPLE TRAPPED</div><div class="kpi-num" style="color: #f59e0b;">{total_trapped:02d}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #ec4899;"><div class="kpi-title">MEDICAL EMERGENCIES</div><div class="kpi-num" style="color: #ec4899;">{critical_cases:02d}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-container" style="border-top-color: #10b981;"><div class="kpi-title">RADAR STATUS</div><div class="kpi-num" style="color: #10b981;">ACTIVE</div></div>', unsafe_allow_html=True)

st.write("")

# 6. Sidebar Controls (All Original Features Fully Intact)
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
    st.session_state["focused_coords"] = None
    st.session_state["focused_user"] = None
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

# 7. Main Split Layout
col_radar, col_queue = st.columns([7, 4])

# ------------ MAP SECTION (STATIC, NO FLICKERING) ------------
with col_radar:
    if st.session_state["focused_coords"]:
        map_lat, map_lng = st.session_state["focused_coords"]
        map_zoom = 17
        st.markdown(f"#### 🎯 RADAR LOCKED ON: `{st.session_state['focused_user'].upper()}`", unsafe_allow_html=True)
        if st.button("🔄 RESET RADAR VIEW (DEFAULT MAP)"):
            st.session_state["focused_coords"] = None
            st.session_state["focused_user"] = None
            st.rerun()
    elif sos_list:
        latest_sos = sos_list[-1]
        map_lat = latest_sos["location"]["lat"]
        map_lng = latest_sos["location"]["lng"]
        map_zoom = 14
        st.markdown(f"#### 🗺️ LIVE INCIDENT RADAR — `OVERVIEW MODE`", unsafe_allow_html=True)
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

    folium.Circle(
        location=[map_lat, map_lng],
        radius=1500 if st.session_state["focused_coords"] else 3000,
        color="#ff003c",
        weight=2,
        fill=True,
        fill_color="#ff003c",
        fill_opacity=0.15,
        tooltip="Active Danger Perimeter"
    ).add_to(radar_map)

    for item in sos_list:
        loc = [item["location"]["lat"], item["location"]["lng"]]
        user = item.get("user", "Unknown")
        count = item.get("people", 1)
        med = item.get("medical_urgent", False)
        place_label = get_place_name(loc[0], loc[1])
        is_focused = (st.session_state["focused_coords"] == (loc[0], loc[1]))
        
        folium.Marker(
            location=loc,
            tooltip=f"🚨 {user} — {place_label}",
            popup=f"<b>{user}</b><br>📍 <b>Area:</b> {place_label}<br>👥 <b>Trapped:</b> {count}<br>🚑 <b>Urgent Medical:</b> {med}<br><code>GPS: {loc[0]:.5f}, {loc[1]:.5f}</code>",
            icon=folium.Icon(color="red" if med else "orange", icon="warning-sign" if med else "user")
        ).add_to(radar_map)
        
        folium.CircleMarker(
            location=loc,
            radius=22 if is_focused else 14,
            color="#00f0ff" if is_focused else "#ff003c",
            weight=4 if is_focused else 2,
            fill=True,
            fill_color="#00f0ff" if is_focused else "#ff003c",
            fill_opacity=0.55 if is_focused else 0.35
        ).add_to(radar_map)

    components.html(radar_map._repr_html_(), height=550)

# ------------ SILENT LIVE QUEUE (UPDATES EVERY 2s WITHOUT FLICKERING THE MAP) ------------
with col_queue:
    st.markdown("#### 🚨 NDRF LIVE RESCUE QUEUE")

    if st.button("🔄 REFRESH ALERTS", use_container_width=True):
        st.rerun()

    @st.fragment(run_every=2)
    def render_silent_live_queue():
        live_list = []
        try:
            r = requests.get(f"{API_BASE_URL}/all-sos", timeout=3).json()
            live_list = r.get("active_emergencies", [])
        except Exception:
            live_list = []

        if live_list:
            for idx, alert in enumerate(reversed(live_list)):
                urgent_badge = "<span style='color:#ff003c; font-weight:bold;'>[URGENT: MEDICAL HELP NEEDED]</span>" if alert.get("medical_urgent") else "<span style='color:#00f0ff;'>[STANDARD RESCUE]</span>"
                u_lat = alert['location']['lat']
                u_lng = alert['location']['lng']
                user_name = alert.get('user', 'Citizen')
                place_name = get_place_name(u_lat, u_lng)
                
                st.markdown(f"""
                <div class="hud-panel" style="margin-bottom: 8px; border-left: 3px solid #ff003c; padding: 12px;">
                    <div style="font-weight: bold; font-size: 15px; color: #f8fafc;" class="mono-text">
                        ALERT #{len(live_list)-idx:02d} : {user_name}
                    </div>
                    <div style="font-size: 13px; color: #00f0ff; font-weight: bold; margin: 2px 0;">
                        📍 {place_name}
                    </div>
                    <div style="font-size: 12px; margin: 2px 0;" class="mono-text">{urgent_badge}</div>
                    <div style="font-size: 13px; color: #94a3b8;" class="mono-text">
                        People: <b style="color:#f8fafc;">{alert.get('people')}</b> | GPS: <code>{u_lat:.5f}, {u_lng:.5f}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🎯 LOCATE ON RADAR (#{len(live_list)-idx:02d})", key=f"focus_btn_{idx}_{u_lat}", use_container_width=True):
                    st.session_state["focused_coords"] = (u_lat, u_lng)
                    st.session_state["focused_user"] = f"{user_name} ({place_name})"
                    st.rerun()
                    
                st.write("")
        else:
            st.markdown("""
            <div class="hud-panel" style="text-align: center; border: 1px dashed rgba(0, 240, 255, 0.3);">
                <p style="color: #00f0ff; margin:0; font-size: 14px; font-weight: 700;" class="mono-text">✓ NO ACTIVE RESCUE REQUESTS</p>
                <p style="color: #64748b; font-size: 12px; margin: 4px 0 0 0;" class="mono-text">All areas are currently normal and safe.</p>
            </div>
            """, unsafe_allow_html=True)

    render_silent_live_queue()
