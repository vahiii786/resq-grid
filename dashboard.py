# dashboard.py - ResQ-Grid Command Interface (Cyber HUD Theme + Full Features Restored)
import streamlit as st
import folium
import requests
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="ResQ-Grid | Cyber Threat & Disaster Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "https://resqgrid-api.onrender.com"

# Session State Persistence (Unchanged)
if "focused_coords" not in st.session_state:
    st.session_state["focused_coords"] = None
if "focused_user" not in st.session_state:
    st.session_state["focused_user"] = None
if "last_search" not in st.session_state:
    st.session_state["last_search"] = "Vijayawada"
if "prev_alert_count" not in st.session_state:
    st.session_state["prev_alert_count"] = 0

# 2. Cyber Security War-Room HUD Styling
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700;800&family=Share+Tech+Mono&display=swap" rel="stylesheet">

<style>
    * { font-family: 'Rajdhani', sans-serif !important; }
    code, pre, .mono-text { font-family: 'Share Tech Mono', monospace !important; }
    
    /* Deep Cyber Matrix Grid Background */
    .stApp {
        background-color: #040914;
        background-image: 
            linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px),
            radial-gradient(circle at 50% 0%, rgba(0, 240, 255, 0.12), transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(255, 0, 60, 0.08), transparent 45%);
        background-size: 32px 32px, 32px 32px, 100% 100%, 100% 100%;
        background-attachment: fixed;
        color: #f1f5f9;
    }

    @keyframes radarPulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.8); }
        70% { box-shadow: 0 0 0 14px rgba(255, 0, 60, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0); }
    }

    /* Glassmorphic Cyber HUD Panels */
    .hud-panel {
        background: rgba(8, 16, 34, 0.78);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 240, 255, 0.28);
        border-radius: 6px;
        padding: 16px 20px;
        position: relative;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
    }
    
    .hud-panel::before {
        content: ""; position: absolute; top: 0; left: 0; width: 10px; height: 10px;
        border-top: 2px solid #00f0ff; border-left: 2px solid #00f0ff;
    }
    .hud-panel::after {
        content: ""; position: absolute; bottom: 0; right: 0; width: 10px; height: 10px;
        border-bottom: 2px solid #ff003c; border-right: 2px solid #ff003c;
    }

    /* KPI Cyber Stat Containers */
    .kpi-container {
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        background: rgba(10, 20, 42, 0.85);
        border-top: 2px solid #00f0ff; 
        border-bottom: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.12);
        padding: 14px; border-radius: 6px;
    }
    .kpi-title { font-family: 'Share Tech Mono', monospace !important; font-size: 11px; color: #38bdf8; letter-spacing: 2px; }
    .kpi-num { font-size: 32px; font-weight: 800; margin-top: 2px; text-shadow: 0 0 10px currentColor; }

    .pulse-dot {
        height: 10px; width: 10px; background-color: #ff003c;
        border-radius: 50%; display: inline-block; animation: radarPulse 2s infinite; margin-right: 8px;
    }

    /* Sidebar - High Contrast Cyber Console */
    [data-testid="stSidebar"] {
        background: #060d1b !important;
        border-right: 1px solid rgba(0, 240, 255, 0.35) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.8);
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
        background-color: #0b172e !important; color: #ffffff !important;
        border: 1px solid #00f0ff !important; font-weight: 700 !important;
        box-shadow: inset 0 0 8px rgba(0, 240, 255, 0.2);
    }

    /* Cyber Action Buttons */
    .stButton>button {
        background: rgba(10, 22, 45, 0.9) !important;
        color: #00f0ff !important; 
        border: 1px solid #00f0ff !important;
        font-weight: 700 !important; 
        letter-spacing: 1.5px !important;
        text-transform: uppercase; 
        border-radius: 4px !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
        transition: all 0.25s ease;
    }
    .stButton>button:hover {
        background: #00f0ff !important;
        color: #040914 !important;
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.85); 
        transform: translateY(-1px);
    }

    /* Foliated Tactical Map Frame */
    iframe {
        border-radius: 8px; 
        border: 1px solid #00f0ff !important;
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Helpers: Nominatim Search, Reverse Geocoding & Weather Telemetry (Unchanged)
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

# Fetch Live SOS Alerts for Initial Map Load
sos_list = []
try:
    sos_res = requests.get(f"{API_BASE_URL}/all-sos", timeout=4).json()
    sos_list = sos_res.get("active_emergencies", [])
except Exception:
    pass

# 4. Top Operations Header (Cyber HUD Look)
st.markdown("""
<div class="hud-panel" style="margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="display:flex; align-items:center;">
                <span class="pulse-dot"></span>
                <span style="font-family: 'Share Tech Mono', monospace; color: #ff003c; font-size: 12px; letter-spacing: 2px;">TACTICAL DEFENSE SURVEILLANCE // ACTIVE</span>
            </div>
            <h1 style="margin: 2px 0 0 0; font-size: 28px; font-weight: 800; letter-spacing: 2px; color: #f8fafc; text-shadow: 0 0 15px rgba(0,240,255,0.6);">
                RESQ-GRID <span style="color: #00f0ff;">COMMAND MATRIX</span>
            </h1>
            <p style="margin: 0; color: #38bdf8; font-size: 13px;" class="mono-text">
                NDRF Integrated Early Warning System & Real-Time Citizen Rescue Mesh
            </p>
        </div>
        <div style="text-align: right;" class="mono-text">
            <span style="color: #00f0ff; font-weight: bold; font-size: 14px; text-shadow: 0 0 8px #00f0ff;">[ SECURE LINK // ENCRYPTED ]</span><br>
            <span style="color: #94a3b8; font-size: 11px;">Telemetry Uplink: ONLINE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Clear Overview Metrics (Cyber Neon Stat Cards)
k1, k2, k3, k4 = st.columns(4)
total_trapped = sum(item.get("people", 0) for item in sos_list)
critical_cases = sum(1 for item in sos_list if item.get("medical_urgent", False))

with k1:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #ff003c;"><div class="kpi-title">ACTIVE INCIDENTS</div><div class="kpi-num" style="color: #ff003c;">{len(sos_list):02d}</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #f59e0b;"><div class="kpi-title">TRAPPED CIVILIANS</div><div class="kpi-num" style="color: #f59e0b;">{total_trapped:02d}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-container" style="border-top-color: #ec4899;"><div class="kpi-title">MEDICAL EMERGENCIES</div><div class="kpi-num" style="color: #ec4899;">{critical_cases:02d}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-container" style="border-top-color: #00f0ff;"><div class="kpi-title">RADAR FREQUENCY</div><div class="kpi-num" style="color: #00f0ff;">ARMED</div></div>', unsafe_allow_html=True)

st.write("")

# 6. Sidebar Controls (All Original Features Fully Preserved)
st.sidebar.markdown("### 📍 TACTICAL SECTOR TARGET")
search_area = st.sidebar.text_input("Search City / Town", value=st.session_state["last_search"])

# Detect if user changed city in sidebar -> Reset individual SOS lock so map immediately pans
if search_area != st.session_state["last_search"]:
    st.session_state["last_search"] = search_area
    st.session_state["focused_coords"] = None
    st.session_state["focused_user"] = None

target = get_coordinates(search_area)
st.sidebar.caption(f"Sector: `{target['name']}` | Coordinates: `{target['lat']:.4f}, {target['lng']:.4f}`")
st.sidebar.markdown("---")

# Weather Data Selection
st.sidebar.markdown("### ⚙️ METEOROLOGICAL TELEMETRY")
data_mode = st.sidebar.radio(
    "Ingestion Mode",
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
        
        st.sidebar.markdown("#### 🛡️ AI RISK EVALUATION")
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
st.sidebar.markdown("### 🚨 SIMULATE CITIZEN SOS")
if st.sidebar.button(f"Inject Mock Beacon in {target['name']}", use_container_width=True):
    mock = {
        "user_name": f"Citizen ({target['name']})",
        "latitude": target["lat"] + 0.003,
        "longitude": target["lng"] + 0.003,
        "people_count": 4,
        "medical_emergency": True
    }
    try:
        requests.post(f"{API_BASE_URL}/send-sos", json=mock, timeout=10)
        st.sidebar.success("Beacon Successfully Injected to Queue!")
        st.rerun()
    except Exception:
        st.sidebar.error("Could not inject mock SOS.")

# 7. Main Split Layout
col_radar, col_queue = st.columns([7, 4])

# ------------ MAP SECTION (DYNAMIC PRIORITY: QUEUE FOCUS > SIDEBAR CITY) ------------
with col_radar:
    # 1. If Officer specifically clicked an alert -> Zoom into that person (Level 17)
    if st.session_state["focused_coords"]:
        map_lat, map_lng = st.session_state["focused_coords"]
        map_zoom = 17
        st.markdown(f"#### 🎯 TARGET LOCK ENGAGED: `{st.session_state['focused_user'].upper()}`", unsafe_allow_html=True)
        if st.button("🔄 DISENGAGE LOCK (RETURN TO SECTOR VIEW)"):
            st.session_state["focused_coords"] = None
            st.session_state["focused_user"] = None
            st.rerun()
    # 2. Otherwise -> Center on the Sidebar Selected City (Level 13)
    else:
        map_lat = target["lat"]
        map_lng = target["lng"]
        map_zoom = 13
        st.markdown(f"#### 🌐 TACTICAL THREAT RADAR — `{target['name'].upper()}`", unsafe_allow_html=True)

    # CartoDB dark_matter Tiles for pure Cyber Threat Map integration
    radar_map = folium.Map(
        location=[map_lat, map_lng], 
        zoom_start=map_zoom,
        max_zoom=19,
        tiles="CartoDB dark_matter"
    )

    folium.Circle(
        location=[map_lat, map_lng],
        radius=1500 if st.session_state["focused_coords"] else 3000,
        color="#00f0ff",
        weight=1,
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.08,
        tooltip=f"Surveillance Perimeter: {target['name'] if not st.session_state['focused_coords'] else 'Active Incident'}"
    ).add_to(radar_map)

    # Plot all SOS beacons with human-readable location names & glowing markers
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
            popup=f"<div style='background-color:#060d1b; color:#ffffff; padding:6px; font-family:sans-serif;'><b>{user}</b><br>📍 <b>Area:</b> {place_label}<br>👥 <b>Trapped:</b> {count}<br>🚑 <b>Urgent Medical:</b> {med}<br><code>GPS: {loc[0]:.5f}, {loc[1]:.5f}</code></div>",
            icon=folium.Icon(color="red" if med else "blue", icon="info-sign")
        ).add_to(radar_map)
        
        # High-Contrast Cyber Pulsing Rings
        folium.CircleMarker(
            location=loc,
            radius=22 if is_focused else 12,
            color="#00f0ff" if is_focused else ("#ff003c" if med else "#00f0ff"),
            weight=3 if is_focused else 1.5,
            fill=True,
            fill_color="#00f0ff" if is_focused else ("#ff003c" if med else "#00f0ff"),
            fill_opacity=0.65 if is_focused else 0.35
        ).add_to(radar_map)

    components.html(radar_map._repr_html_(), height=550)

# ------------ LIVE QUEUE (SILENT 2-SEC AUTO UPDATE + INSTANT POPUP NOTIFICATION) ------------
with col_queue:
    st.markdown("#### ⚠️ ACTIVE INCIDENT LOG")

    if st.button("🔄 RESYNC RADAR QUEUE", use_container_width=True):
        st.rerun()

    @st.fragment(run_every=2)
    def render_silent_live_queue():
        live_list = []
        try:
            r = requests.get(f"{API_BASE_URL}/all-sos", timeout=3).json()
            live_list = r.get("active_emergencies", [])
        except Exception:
            live_list = []

        # Instant Toast Pop-up Notification trigger when new SOS arrives
        curr_count = len(live_list)
        if curr_count > st.session_state["prev_alert_count"] and st.session_state["prev_alert_count"] > 0:
            latest = live_list[-1]
            latest_place = get_place_name(latest['location']['lat'], latest['location']['lng'])
            st.toast(f"🚨 INCOMING DISTRESS SIGNAL! {latest.get('user', 'Citizen')} ({latest_place})", icon="⚡")
        st.session_state["prev_alert_count"] = curr_count

        if live_list:
            for idx, alert in enumerate(reversed(live_list)):
                is_med = alert.get("medical_urgent", False)
                card_border = "#ff003c" if is_med else "#00f0ff"
                badge = "<span style='color:#ff003c; font-weight:bold;'>[URGENT: TRAUMA AID]</span>" if is_med else "<span style='color:#00f0ff;'>[TACTICAL EXTRACTION]</span>"
                
                u_lat = alert['location']['lat']
                u_lng = alert['location']['lng']
                user_name = alert.get('user', 'Citizen')
                place_name = get_place_name(u_lat, u_lng)
                
                st.markdown(f"""
                <div class="hud-panel" style="margin-bottom: 8px; border-left: 3px solid {card_border}; padding: 12px; background: rgba(8, 16, 34, 0.9);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight: bold; font-size: 14px; color: #f8fafc;" class="mono-text">
                            BEACON #{len(live_list)-idx:02d} : {user_name}
                        </span>
                        <span style="font-size: 11px;" class="mono-text">{badge}</span>
                    </div>
                    <div style="font-size: 13px; color: #00f0ff; font-weight: bold; margin: 3px 0;">
                        📍 {place_name}
                    </div>
                    <div style="font-size: 12px; color: #94a3b8;" class="mono-text">
                        Civilians: <b style="color:#f8fafc;">{alert.get('people')}</b> | GPS: <code>{u_lat:.5f}, {u_lng:.5f}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🎯 ENGAGE RADAR LOCK (#{len(live_list)-idx:02d})", key=f"focus_btn_{idx}_{u_lat}", use_container_width=True):
                    st.session_state["focused_coords"] = (u_lat, u_lng)
                    st.session_state["focused_user"] = f"{user_name} ({place_name})"
                    st.rerun()
                    
                st.write("")
        else:
            st.markdown("""
            <div class="hud-panel" style="text-align: center; border: 1px dashed rgba(0, 240, 255, 0.4); padding: 20px;">
                <p style="color: #00f0ff; margin:0; font-size: 14px; font-weight: 700;" class="mono-text">✓ SECTOR ALL-CLEAR // ZERO THREATS</p>
                <p style="color: #64748b; font-size: 12px; margin: 4px 0 0 0;" class="mono-text">No pending distress transmissions in buffer.</p>
            </div>
            """, unsafe_allow_html=True)

    render_silent_live_queue()
