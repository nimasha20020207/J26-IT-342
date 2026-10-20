import numpy as np
import pandas as pd

def map_difficulty(val):
    return {'Easy': 1, 'Moderate': 2, 'Hard': 3}.get(val, 2)

def extract_scenic_tags(val):
    if pd.isna(val):
        return set()
    tags = set()
    s = str(val)
    for kw in ['Waterfalls', 'Dense Forests', 'Panoramic Mountain Views', 'Caves', 'Tea Estates', 'Historic / Cultural Sites']:
        if kw in s or (kw == 'Dense Forests' and 'Forest' in s):
            tags.add(kw)
    return tags

def build_route_geometry_from_csv(row):
    s_lat = float(row['Start_Lat'])
    s_lng = float(row['Start_Lon'])
    e_lat = float(row['End_Lat'])
    e_lng = float(row['End_Lon'])
    dist_km = float(row['Distance_KM'])

    steep_start = float(row['Steep_Start_KM']) if 'Steep_Start_KM' in row and not pd.isna(row['Steep_Start_KM']) else round(dist_km * 0.35, 1)
    steep_end = float(row['Steep_End_KM']) if 'Steep_End_KM' in row and not pd.isna(row['Steep_End_KM']) else round(dist_km * 0.55, 1)

    num_pts = 12
    route_points = []
    elev_profile = []

    for i in range(num_pts):
        t = i / (num_pts - 1)
        curve_offset = np.sin(t * np.pi * 2) * 0.0018
        lat = round(float(s_lat + (e_lat - s_lat) * t + curve_offset), 5)
        lng = round(float(s_lng + (e_lng - s_lng) * t - curve_offset * 0.7), 5)
        route_points.append({"lat": lat, "lng": lng})

        norm_h = round(float(0.15 + 0.80 * np.sin(t * np.pi * 0.85)), 2)
        elev_profile.append(norm_h)

    return {
        "start_lat": s_lat,
        "start_lng": s_lng,
        "summit_lat": e_lat,
        "summit_lng": e_lng,
        "gpx_file_path": str(row.get('GPX_File_Path', '')),
        "route_points": route_points,
        "steep_segment_indices": [4, 5, 6],
        "steep_label": f"Km {steep_start}-{steep_end} High Incline",
        "elevation_profile": elev_profile
    }