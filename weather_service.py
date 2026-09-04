# weather_service.py - Live Weather Fetcher
import requests

def get_live_rainfall(latitude: float, longitude: float) -> dict:
    """
    Open-Meteo API nunchi live rainfall data (in mm) fetch chesthundi.
    Free API, no secret keys required.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=precipitation,rain&hourly=precipitation&forecast_days=1"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Current rainfall (last 1 hour in mm)
        current_rain = data.get("current", {}).get("precipitation", 0.0)
        
        # Estimated 24h total rainfall sum
        hourly_rain = data.get("hourly", {}).get("precipitation", [])
        rain_24h = sum(hourly_rain) if hourly_rain else current_rain * 24.0
        
        return {
            "status": "success",
            "current_rain_mm": current_rain,
            "estimated_24h_mm": round(rain_24h, 2)
        }
    except Exception as e:
        # Rate limit leda internet issue unte fallback default
        return {
            "status": "error",
            "message": str(e),
            "estimated_24h_mm": 15.0 # baseline safe value
        }