# brain.py - ResQ-Grid AI Risk Calculator

def assess_flood_risk(rainfall_mm: float, river_level_m: float, elevation_m: float) -> dict:
    """
    Ee function 3 inputs theeskuntundi:
    1. rainfall_mm: 24 hours lo padina varsham (in mm)
    2. river_level_m: Daggarlo unna river/canal water level (in meters)
    3. elevation_m: Aa area height/elevation (in meters)
    
    Output: Risk Score (0 to 100) mariyu Action Plan
    """
    
    # 1. Rainfall score (150mm kante ekkuva unte max 45 points)
    rain_score = min(rainfall_mm / 150.0, 1.0) * 45.0
    
    # 2. River level score (10 meters kante ekkuva unte max 35 points)
    river_score = min(river_level_m / 10.0, 1.0) * 35.0
    
    # 3. Elevation score (Pallam/low area lo unte max 20 points danger)
    elevation_score = max(0.0, (100.0 - min(elevation_m, 100.0)) / 100.0) * 20.0
    
    # Total Risk Score (0 nunchi 100 madhyalo untundi)
    total_score = round(rain_score + river_score + elevation_score, 1)
    
    # Severity Decision
    if total_score >= 70.0:
        level = "CRITICAL"
        action = "High flood risk! NDRF rescue team alert & immediate evacuation needed."
    elif total_score >= 40.0:
        level = "ALERT"
        action = "Moderate risk. Water levels peruguthunnayi, people alert ga undali."
    else:
        level = "SAFE"
        action = "Area safe ga undi. Regular monitoring continue cheyandi."
        
    return {
        "risk_score": total_score,
        "level": level,
        "action": action
    }

# Code correct ga panichesthundo ledo test cheyadaniki chinna test run:
if __name__ == "__main__":
    print("--- TESTING FLOOD RISK LOGIC ---")
    # Example: Heavy rain (140mm), High river level (8.5m), Low elevation area (15m)
    test_result = assess_flood_risk(rainfall_mm=140.0, river_level_m=8.5, elevation_m=15.0)
    print("Risk Score:", test_result["risk_score"])
    print("Level     :", test_result["level"])
    print("Action    :", test_result["action"])