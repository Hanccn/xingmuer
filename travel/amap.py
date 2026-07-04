import requests
from django.conf import settings

BASE = "https://restapi.amap.com/v3"
KEY = settings.AMAP_KEY

def _get(path, params):
    if not KEY:
        return {}
    params["key"] = KEY
    try:
        r = requests.get(f"{BASE}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError):
        return {}

def search_poi(keywords, city=None, types="风景名胜", page=1, offset=20):
    p = {"keywords": keywords, "types": types, "offset": offset, "page": page, "extensions": "all"}
    if city: p["city"] = city
    data = _get("/place/text", p)
    return data.get("pois", []) if data.get("status") == "1" else []

def search_around(lng, lat, keywords="", types="风景名胜", radius=5000, offset=20):
    p = {"location": f"{lng},{lat}", "keywords": keywords, "types": types, "radius": radius, "offset": offset, "extensions": "all"}
    data = _get("/place/around", p)
    return data.get("pois", []) if data.get("status") == "1" else []

def distance_matrix(origins, destination):
    """origins: "lng1,lat1|lng2,lat2", destination: "lng,lat" """
    p = {"origins": origins, "destination": destination, "type": "1"}
    data = _get("/distance", p)
    return data.get("results", []) if data.get("status") == "1" else []

def direction(origin, destination, mode="driving"):
    """origin/destination: "lng,lat" """
    p = {"origin": origin, "destination": destination, "extensions": "all"}
    path = "/direction/driving" if mode == "driving" else "/direction/transit/integrated"
    data = _get(path, p)
    if data.get("status") == "1":
        route = data.get("route", {})
        paths = route.get("paths", [])
        return paths[0] if paths else {}
    return {}

def geocode(address, city=None):
    p = {"address": address}
    if city: p["city"] = city
    data = _get("/geocode/geo", p)
    geos = data.get("geocodes", []) if data.get("status") == "1" else []
    return geos[0] if geos else {}

def weather(city_code):
    data = _get("/weather/weatherInfo", {"city": city_code, "extensions": "all"})
    return data.get("forecasts", []) if data.get("status") == "1" else []
