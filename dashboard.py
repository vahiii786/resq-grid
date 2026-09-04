# dashboard.py - ResQ-Grid Command Interface (Rock-Solid Static Map + Silent Live Queue)
import streamlit as st
import folium
import requests
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="ResQ-Grid | Tactical Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "https://resqgrid-api.onrender.com"

# Session States
if "focused_coords" not in st.session_state:
    st.session_state["focused_coords"] = None
if "focused_user" not in st.session_state:
    st.session_state["focused_user"] = None
if "last_search" not in st.session_state:
    st.session_state["last_search"] = "Vijayawada"

# 2. High-Tech Styling
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
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.8); }
        70% { box-shadow: 0 0 0 14px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    
    .hud-panel {
        background: rgba(10, 15, 29, 0.85);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(0, 240, 255, 0.22);
        border-radius: 8px;
        padding: 14px 18px;
        position: relative;
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
        border-top: 2px solid #00f0ff; padding: 12px; border-radius: 6px;
    }
    .kpi-title { font-family: 'Share Tech Mono', monospace !important; font-size: 11px; color: #94a3b8; letter-spacing: 2px; }
    .kpi-num { font-size: 30px; font-weight: 800; margin-top: 2px; }
    
    .pulse-dot {
        height: 10px; width: 10px; background-color: #ef4444;
        border-radius: 50%; display: inline-block; animation: radarPulse 1.5s infinite; margin-right: 8px;
    }
    
    [data-testid="stSidebar"] {
        background: #040711 !important;
        border-right: 1px solid rgba(0, 240, 255, 0.3) !important;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] input { background-color: #0b1329 !important; border: 1px solid #00f0ff !important; }
    
    .stButton>button {
        background: linear-gradient(90deg, #b91c1c 0%, #7f1d1d 100%) !important;
        color: #ffffff !important; border: 1px solid #ef4444 !important; font-weight: 700 !important;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #dc2626 0%, #991b1b 100%) !important;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
    }
    iframe { border-radius: 8px; border: 1px solid rgba(0, 240, 255, 0.25) !important; }
</style>
""", unsafe_allow_html=True)

# 3. Helpers
@st.cache_data(ttl=3600)
def get_coordinates(query: str):
    url = f"https://nominatim.openstreetmap.org/search?q={query},India&format=json&limit=1"
    headers = {"User-Agent": "ResQGrid-TacticalEngine"}
    try:
        res = requests.get(url, headers=headers, timeout=4).json()
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
        res = requests.get(url, headers=headers, timeout=3).json()
        addr = res.get("address", {})
        suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("residential") or addr.get("road")
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county")
        if suburb and city:
            return f"{suburb}, {city}"
        elif city:
            return city
        return ", ".join(res.get("display_name", "").split(",")[:2])
    except Exception:
        return f"{lat:.3f}, {lon:.3f}"

# Fetch Baseline SOS Data
sos_list = []
try:
    sos_res = requests.get(f"{API_BASE_URL}/all-sos", timeout=3).json()
    sos_list = sos_res.get("active_emergencies", [])
except Exception:
    pass

# 4. Top Operations Header (Static)
st.markdown("""
<div class="hud-panel" style="margin-bottom: 16px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="display:flex; align-items:center;">
                <span class="pulse-dot"></span>
                <span style="font-family: 'Share Tech Mono', monospace; color: #ef4444; font-size: 12px; letter-spacing: 2px;">TACTICAL LIVE MESH</span>
            </div>
            <h1 style="margin: 2px 0 0 0; font-size: 26px; font-weight: 800; color: #f8fafc;">
                RESQ-GRID <span style="color: #00f0ff;">COMMAND CENTER</span>
            </h1>
        </div>
        <div style="text-align: right;" class="mono-text">
            <span style="color: #00f0ff; font-weight: bold; font-size: 13px;">[ SYSTEM STABLE ]</span><br>
            <span style="color: #10b981; font-size: 11px;">● Silent Queue Polling Active</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar Controls (Static)
st.sidebar.markdown("### 📍 SELECT BASE SECTOR")
search_area = st.sidebar.text_input("Enter City / District", value=st.session_state["last_search"])

if search_area != st.session_state["last_search"]:
    st.session_state["last_search"] = search_area
    st.session_state["focused_coords"] = None
    st.session_state["focused_user"] = None

target = get_coordinates(search_area)
st.sidebar.caption(f"Sector: `{target['name']}` | GPS: `{target['lat']:.4f}, {target['lng']:.4f}`")
st.sidebar.markdown("---")

if st.sidebar.button("⚡ CHECK SECTOR FLOOD RISK", use_container_width=True):
    st.session_state["focused_coords"] = None
    payload = {"area_name": target["name"], "rainfall_mm": 120.0, "river_level_m": 6.5, "elevation_m": 15.0}
    try:
        r = requests.post(f"{API_BASE_URL}/check-risk", json=payload, timeout=6).json()
        eval_data = r["result"]
        st.sidebar.error(f"RISK: {eval_data['level']} [{eval_data['risk_score']}]")
        st.sidebar.info(eval_data["action"])
    except Exception:
        st.sidebar.error("Cloud Error")

# 6. Main Layout Split
col_radar, col_queue = st.columns([7, 4])

# ----------------- MAP SECTION (COMPLETELY STATIC - ZERO BLINK) -----------------
with col_radar:
    if st.session_state["focused_coords"]:
        map_lat, map_lng = st.session_state["focused_coords"]
        map_zoom = 17
        st.markdown(f"#### 🎯 RADAR LOCKED: `{st.session_state['focused_user'].upper()}`", unsafe_allow_html=True)
        if st.button("🔄 BACK TO OVERVIEW MAP"):
            st.session_state["focused_coords"] = None
            st.session_state["focused_user"] = None
            st.rerun()
    elif sos_list:
        latest_sos = sos_list[-1]
        map_lat = latest_sos["location"]["lat"]
        map_lng = latest_sos["location"]["lng"]
        map_zoom = 14
        st.markdown(f"#### 🗺️ LIVE INCIDENT RADAR — `SECTOR VIEW`", unsafe_allow_html=True)
    else:
        map_lat = target["lat"]
        map_lng = target["lng"]
        map_zoom = 13
        st.markdown(f"#### 🗺️ SECTOR RADAR — `{target['name'].upper()}`", unsafe_allow_html=True)

    # The Map object renders ONCE and stays rock-solid without flickering
    radar_map = folium.Map(location=[map_lat, map_lng], zoom_start=map_zoom, tiles="OpenStreetMap")

    folium.Circle(
        location=[map_lat, map_lng],
        radius=1200 if st.session_state["focused_coords"] else 2800,
        color="#ff003c", weight=2, fill=True, fill_color="#ff003c", fill_opacity=0.18
    ).add_to(radar_map)

    for item in sos_list:
        loc = [item["location"]["lat"], item["location"]["lng"]]
        user = item.get("user", "Citizen")
        count = item.get("people", 1)
        med = item.get("medical_urgent", False)
        place_label = get_place_name(loc[0], loc[1])
        is_focused = (st.session_state["focused_coords"] == (loc[0], loc[1]))

        folium.Marker(
            location=loc,
            tooltip=f"🚨 {user} ({place_label})",
            popup=f"<b>{user}</b><br>📍 {place_label}<br>👥 Trapped: {count}<br>🚑 Medical: {med}",
            icon=folium.Icon(color="red" if med else "orange", icon="warning-sign" if med else "user")
        ).add_to(radar_map)

        folium.CircleMarker(
            location=loc,
            radius=18 if is_focused else 12,
            color="#00f0ff" if is_focused else "#ff003c",
            weight=3 if is_focused else 2,
            fill=True,
            fill_color="#00f0ff" if is_focused else "#ff003c",
            fill_opacity=0.55 if is_focused else 0.3
        ).add_to(radar_map)

    components.html(radar_map._repr_html_(), height=560)


# ----------- SILENT LIVE AUTO-REFRESH QUEUE (ONLY THIS UPDATES EVERY 2s) -----------
with col_queue:
    st.markdown("#### 🚨 NDRF LIVE RESCUE QUEUE")

    @st.fragment(run_every=2)
    def render_silent_live_queue():
        live_list = []
        try:
            r = requests.get(f"{API_BASE_URL}/all-sos", timeout=3).json()
            live_list = r.get("active_emergencies", [])
        except Exception:
            live_list = []

        # Silent Status Tag
        st.caption(f"⚡ Live Sync Active | Total Distress Beacons: **{len(live_list)}**")

        if live_list:
            for idx, alert in enumerate(reversed(live_list)):
                urgent_badge = "<span style='color:#ff003c; font-weight:bold;'>[URGENT: MEDICAL]</span>" if alert.get("medical_urgent") else "<span style='color:#00f0ff;'>[STANDARD RESCUE]</span>"
                u_lat = alert['location']['lat']
                u_lng = alert['location']['lng']
                user_name = alert.get('user', 'Citizen')
                place_name = get_place_name(u_lat, u_lng)

                st.markdown(f"""
                <div class="hud-panel" style="margin-bottom: 8px; border-left: 3px solid #ff003c; padding: 10px;">
                    <div style="font-weight: bold; font-size: 15px; color: #f8fafc;" class="mono-text">
                        ALERT #{len(live_list)-idx:02d} : {user_name}
                    </div>
                    <div style="font-size: 13px; color: #00f0ff; font-weight: bold; margin: 2px 0;">
                        📍 {place_name}
                    </div>
                    <div style="font-size: 12px; margin: 2px 0;" class="mono-text">{urgent_badge}</div>
                    <div style="font-size: 12px; color: #94a3b8;" class="mono-text">
                        People: <b style="color:#f8fafc;">{alert.get('people')}</b> | GPS: <code>{u_lat:.4f}, {u_lng:.4f}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🎯 LOCATE ON RADAR (#{len(live_list)-idx:02d})", key=f"q_btn_{idx}_{u_lat}", use_container_width=True):
                    st.session_state["focused_coords"] = (u_lat, u_lng)
                    st.session_state["focused_user"] = f"{user_name} - {place_name}"
                    st.rerun()
                st.write("")
        else:
            st.markdown("""
            <div class="hud-panel" style="text-align: center; border: 1px dashed rgba(0, 240, 255, 0.3);">
                <p style="color: #00f0ff; margin:0; font-size: 13px; font-weight: 700;" class="mono-text">✓ NO ACTIVE RESCUE BEACONS</p>
                <p style="color: #64748b; font-size: 11px; margin: 4px 0 0 0;" class="mono-text">Listening for emergency distress signals...</p>
            </div>
            """, unsafe_allow_html=True)

    render_silent_live_queue()
