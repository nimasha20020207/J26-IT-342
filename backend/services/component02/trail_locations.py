"""
trail_locations.py
------------------
Component 02: Reference Coordinates and Terrain Profiles for Sri Lankan Hiking Trails
"""

TRAIL_COORDINATES: dict[str, tuple[float, float]] = {
    "Pidurangala": (7.9662102, 80.7616977),
    "Sigiriya": (7.9566634, 80.7599301),
    "Alagalla": (7.2979754, 80.4715679),
    "Narangala": (7.0367166, 81.0087047),
    "Hanthana": (7.2535386, 80.6279647),
    "Lakegala": (7.4660876, 80.8393578),
    "Manigala": (7.5201609, 80.7671233),
    "Kirigalpoththa": (6.7989937, 80.7664235),
    "Little Adam's peak": (6.8650500, 81.0630167),
    "Pettigala": (7.2863410, 80.7598155),
    "Peacock hills": (7.0852774, 80.6327218),
    "Thotupala kanda": (6.8331199, 80.8197979),
    "Bathalegala": (7.1900861, 80.4338935),
    "Adam's peak": (6.8094, 80.4994),
    "Ella rock": (6.8536, 81.0450),
}

TRAIL_TERRAIN: dict[str, dict] = {
    "Pidurangala": {"elevation_m": 340, "slope_degrees": 25.0, "terrain": "Rock outcrop, boulder scramble"},
    "Sigiriya": {"elevation_m": 349, "slope_degrees": 30.0, "terrain": "Rock fortress, stair climb, exposed rock"},
    "Alagalla": {"elevation_m": 1140, "slope_degrees": 28.0, "terrain": "Grassland ridge, rocky mountain trail"},
    "Narangala": {"elevation_m": 1527, "slope_degrees": 22.0, "terrain": "Montane forest, grassland ridge"},
    "Hanthana": {"elevation_m": 1200, "slope_degrees": 20.0, "terrain": "Forested mountain trail, rolling peaks"},
    "Lakegala": {"elevation_m": 1310, "slope_degrees": 35.0, "terrain": "Steep pyramidal peak, sheer rock faces"},
    "Manigala": {"elevation_m": 1105, "slope_degrees": 18.0, "terrain": "Plateau ridge, forest patch"},
    "Kirigalpoththa": {"elevation_m": 2388, "slope_degrees": 24.0, "terrain": "High-altitude cloud forest, wet bog"},
    "Little Adam's peak": {"elevation_m": 1141, "slope_degrees": 15.0, "terrain": "Tea plantation paths, dirt ridge"},
    "Pettigala": {"elevation_m": 1400, "slope_degrees": 26.0, "terrain": "Dense rainforest, rocky summit"},
    "Peacock hills": {"elevation_m": 1513, "slope_degrees": 18.0, "terrain": "Tea estate trails, forested slope"},
    "Thotupala kanda": {"elevation_m": 2357, "slope_degrees": 20.0, "terrain": "Montane dwarf forest, damp trail"},
    "Bathalegala": {"elevation_m": 797, "slope_degrees": 32.0, "terrain": "Table mountain, sheer sandstone cliffs"},
    "Adam's peak": {"elevation_m": 2243, "slope_degrees": 30.0, "terrain": "Paved steps, steep mountain stairs, cloud forest"},
    "Ella rock": {"elevation_m": 1320, "slope_degrees": 25.0, "terrain": "Eucalyptus forest, railway track, rocky summit"},
}