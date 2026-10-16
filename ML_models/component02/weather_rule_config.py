
{
  "metadata": {
    "purpose": "Experimental weather-only hazard indicators",
    "operational_warning_system": false,
    "threshold_status": "UNSET - requires authoritative sourcing and validation"
  },
  "rules": {
    "landslide": {
      "required_features": [
        "rainfall_24h_mm",
        "rainfall_72h_mm",
        "slope_degrees"
      ],
      "rainfall_24h_threshold_mm": null,
      "rainfall_72h_threshold_mm": null,
      "minimum_slope_degrees": null
    },
    "slippery_trail": {
      "required_features": [
        "rainfall_3h_mm",
        "rainfall_24h_mm"
      ],
      "rainfall_3h_threshold_mm": null,
      "rainfall_24h_threshold_mm": null
    },
    "dense_fog": {
      "required_features": [
        "visibility_m"
      ],
      "maximum_visibility_m": null
    },
    "strong_wind": {
      "required_features": [
        "wind_gust_kmh"
      ],
      "wind_gust_threshold_kmh": null
    }
  }
}
