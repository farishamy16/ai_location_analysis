import os
import requests
from dotenv import load_dotenv

API_KEY = os.getenv("DISTANCEMATRIX_API_KEY")

print(f"API Key exists" if API_KEY else "API Key is None!")


def geocode_address(address: str):
    url = "https://api-v2.distancematrix.ai/maps/api/geocode/json"
    params = {
        "address": address,
        "key": API_KEY,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "OK" or not data.get("result"):
        raise ValueError(f"Geocoding failed: {data.get('status')}")

    first = data["result"][0]
    location = first["geometry"]["location"]
    return {
      "lat": location["lat"],
      "lng": location["lng"],
      "formatted_address": first.get("formatted_address"),
      "raw": first,
    }

# Usage
coords = geocode_address("UiTM Shah Alam")
print(coords)