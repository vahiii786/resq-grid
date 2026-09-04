# server.py - ResQ-Grid API Server
from fastapi import FastAPI
from pydantic import BaseModel
from brain import assess_flood_risk
from weather_service import get_live_rainfall

app = FastAPI(title="ResQ-Grid Disaster System")

# Model schemas (Inputs ela undalo define chestunnam)
class RiskInput(BaseModel):
    area_name: str
    rainfall_mm: float
    river_level_m: float
    elevation_m: float

class SOSInput(BaseModel):
    user_name: str
    latitude: float
    longitude: float
    people_count: int
    medical_emergency: bool

# SOS alerts ni memory lo save cheyadaniki oka empty list
sos_database = []

@app.get("/")
def home():
    return {"message": "ResQ-Grid Server Live lo undi!"}

# 1. Flood Risk Check Endpoint
@app.post("/check-risk")
def check_risk(data: RiskInput):
    # Manam rasina brain.py function ni ikkada call chestunnam
    evaluation = assess_flood_risk(
        rainfall_mm=data.rainfall_mm,
        river_level_m=data.river_level_m,
        elevation_m=data.elevation_m
    )
    return {
        "area": data.area_name,
        "result": evaluation
    }

# 2. People Emergency SOS Send chese Endpoint
@app.post("/send-sos")
def send_sos(data: SOSInput):
    alert_record = {
        "user": data.user_name,
        "location": {"lat": data.latitude, "lng": data.longitude},
        "people": data.people_count,
        "medical_urgent": data.medical_emergency
    }
    sos_database.append(alert_record)
    return {
        "status": "SUCCESS",
        "message": "SOS received! Rescue team alerted.",
        "total_active_sos": len(sos_database)
    }

# 3. Rescue teams anni pending SOS chudataniki Endpoint
@app.get("/all-sos")
def view_all_sos():
    return {"active_emergencies": sos_database}
# Live Coordinates batti direct real-time risk check
@app.get("/live-risk")
def live_risk_by_location(lat: float, lng: float, river_level: float = 3.5, elevation: float = 20.0):
    weather_data = get_live_rainfall(lat, lng)
    live_rain = weather_data["estimated_24h_mm"]
    
    # Assess risk using our brain.py
    evaluation = assess_flood_risk(
        rainfall_mm=live_rain,
        river_level_m=river_level,
        elevation_m=elevation
    )
    
    return {
        "coordinates": {"lat": lat, "lng": lng},
        "live_rainfall_24h_mm": live_rain,
        "evaluation": evaluation
    }