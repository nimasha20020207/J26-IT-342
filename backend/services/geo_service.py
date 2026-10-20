"""
Geospatial Emergency Resource Locator for Sri Lankan Hiking Regions (Component 4)
Uses the Haversine formula to compute distances to verified emergency facilities
(Hospitals, Ranger Stations, Police / STF Rescue, DMC Centers) across major hiking trails.
"""
import math
from typing import List, Dict, Any

# Verified registry of emergency facilities around Sri Lanka's primary hiking trails
SRI_LANKA_EMERGENCY_RESOURCES = [
    # Horton Plains / Nuwara Eliya Area
    {
        "id": "HOSP-001",
        "name": "Nuwara Eliya District General Hospital",
        "type": "Hospital",
        "latitude": 6.9707,
        "longitude": 80.7828,
        "phone": "+94 52 222 2261",
        "trail_area": "Horton_Plains",
        "services": ["Emergency Trauma Unit", "ICU", "Ambulance Dispatch"]
    },
    {
        "id": "RANG-001",
        "name": "Horton Plains National Park Ranger Station (DWC)",
        "type": "Ranger Post",
        "latitude": 6.8096,
        "longitude": 80.8028,
        "phone": "+94 52 223 4411",
        "trail_area": "Horton_Plains",
        "services": ["Wilderness Search & Rescue", "First Aid Post", "Evacuation Patrol"]
    },
    {
        "id": "POL-001",
        "name": "Nuwara Eliya Police Station",
        "type": "Police",
        "latitude": 6.9698,
        "longitude": 80.7725,
        "phone": "+94 52 222 2222",
        "trail_area": "Horton_Plains",
        "services": ["Emergency Response", "Search Coordination"]
    },

    # Knuckles / Riverston Area
    {
        "id": "HOSP-002",
        "name": "Matale District General Hospital",
        "type": "Hospital",
        "latitude": 7.4674,
        "longitude": 80.6234,
        "phone": "+94 66 222 2261",
        "trail_area": "Knuckles",
        "services": ["Emergency Trauma Unit", "Surgical Ward", "Ambulance"]
    },
    {
        "id": "RANG-002",
        "name": "Riverston Illukkumbura Forest Department Centre",
        "type": "Ranger Post",
        "latitude": 7.5310,
        "longitude": 80.7620,
        "phone": "+94 66 224 8171",
        "trail_area": "Riverston",
        "services": ["Forest Range Officer", "Mountain Rescue Support", "Trail Guide Dispatch"]
    },
    {
        "id": "RANG-003",
        "name": "Knuckles Deanston Conservation Centre",
        "type": "Ranger Post",
        "latitude": 7.3235,
        "longitude": 80.8492,
        "phone": "+94 81 237 4160",
        "trail_area": "Knuckles",
        "services": ["Wilderness Guide Assistance", "Emergency VHF Radio", "First Aid"]
    },

    # Adam's Peak (Sri Pada) Area
    {
        "id": "HOSP-003",
        "name": "Maskeliya District Hospital",
        "type": "Hospital",
        "latitude": 6.8320,
        "longitude": 80.5730,
        "phone": "+94 51 223 0261",
        "trail_area": "Adam_Peak",
        "services": ["Emergency Ward", "Trauma Stabilization", "Ambulance"]
    },
    {
        "id": "POL-002",
        "name": "Nallathanniya Police & Special Rescue Post",
        "type": "Police / STF",
        "latitude": 6.8197,
        "longitude": 80.5231,
        "phone": "+94 52 225 9422",
        "trail_area": "Adam_Peak",
        "services": ["Mountain Search & Rescue", "Stretcher Team", "Disaster Unit"]
    },

    # Ella Rock / Little Adam's Peak Area
    {
        "id": "HOSP-004",
        "name": "Badulla Provincial General Hospital",
        "type": "Hospital",
        "latitude": 6.9895,
        "longitude": 81.0560,
        "phone": "+94 55 222 2261",
        "trail_area": "Ella_Rock",
        "services": ["Tertiary Trauma Care", "Neuro-Trauma Unit", "Helipad Access"]
    },
    {
        "id": "POL-003",
        "name": "Ella Tourist Police Post",
        "type": "Police",
        "latitude": 6.8712,
        "longitude": 81.0475,
        "phone": "+94 57 222 8555",
        "trail_area": "Ella_Rock",
        "services": ["Tourist Safety Response", "Local Guides Association Dispatch"]
    },

    # Sinharaja Rain Forest Area
    {
        "id": "HOSP-005",
        "name": "Kalawana Base Hospital",
        "type": "Hospital",
        "latitude": 6.5312,
        "longitude": 80.4021,
        "phone": "+94 45 225 5261",
        "trail_area": "Sinharaja",
        "services": ["Snake Bite / Toxin Unit", "Emergency Care", "Ambulance"]
    },
    {
        "id": "RANG-004",
        "name": "Sinharaja Kudawa Forest Conservation Station",
        "type": "Ranger Post",
        "latitude": 6.4385,
        "longitude": 80.4172,
        "phone": "+94 45 345 5188",
        "trail_area": "Sinharaja",
        "services": ["Rainforest Rescue Guides", "Forestry Officers", "VHF Comms"]
    },

    # Pidurangala / Sigiriya Area
    {
        "id": "HOSP-006",
        "name": "Dambulla Base Hospital",
        "type": "Hospital",
        "latitude": 7.8742,
        "longitude": 80.6511,
        "phone": "+94 66 228 4761",
        "trail_area": "Pidurangala",
        "services": ["Emergency Trauma Treatment", "Ambulance Service"]
    },
    {
        "id": "POL-004",
        "name": "Sigiriya Tourist Police Station",
        "type": "Police",
        "latitude": 7.9542,
        "longitude": 80.7570,
        "phone": "+94 66 228 6555",
        "trail_area": "Pidurangala",
        "services": ["Rock Climbing Rescue Support", "Emergency Assistance"]
    }
]

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS points using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def estimate_travel_time_minutes(distance_km: float, is_wilderness: bool = True) -> int:
    """
    Estimates emergency dispatch/travel time taking mountain road & trail terrain into account.
    Average mountain vehicle speed ~ 25-30 km/h, on-foot trail access ~ 4 km/h.
    """
    if is_wilderness:
        # Blended vehicle + foot response speed ~ 20 km/h
        hours = distance_km / 20.0
    else:
        hours = distance_km / 40.0
    return max(5, int(round(hours * 60)))

class GeoEmergencyService:
    @staticmethod
    def find_nearest_resources(
        user_lat: float,
        user_lon: float,
        limit: int = 5,
        resource_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Calculates distances to all registered emergency facilities, sorts by proximity,
        and returns the top closest resources with estimated arrival times.
        """
        results = []
        for res in SRI_LANKA_EMERGENCY_RESOURCES:
            if resource_type and res["type"].lower() != resource_type.lower():
                continue
            
            dist = haversine_distance_km(user_lat, user_lon, res["latitude"], res["longitude"])
            est_time = estimate_travel_time_minutes(dist)

            results.append({
                "id": res["id"],
                "name": res["name"],
                "type": res["type"],
                "distance_km": dist,
                "distance_str": f"{dist:.1f} km",
                "estimated_time_mins": est_time,
                "estimated_time_str": f"{est_time} mins",
                "phone": res["phone"],
                "latitude": res["latitude"],
                "longitude": res["longitude"],
                "trail_area": res["trail_area"],
                "services": res.get("services", [])
            })

        # Sort by distance ascending
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

if __name__ == "__main__":
    # Test with Horton Plains World's End coordinates (6.809, 80.803)
    service = GeoEmergencyService()
    nearest = service.find_nearest_resources(6.809, 80.803, limit=4)
    print("Nearest resources to Horton Plains:")
    for n in nearest:
        print(f" - {n['name']} ({n['type']}): {n['distance_str']}, ~{n['estimated_time_str']}, Tel: {n['phone']}")
