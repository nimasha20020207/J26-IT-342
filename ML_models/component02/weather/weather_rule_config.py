
# Example configuration (commented out):
#   "metadata": {
#     "purpose": "Experimental weather-only hazard indicators",
#     "operational_warning_system": false,
#     "threshold_status": "UNSET - requires authoritative sourcing and validation"
#   },
#   "rules": {
#     "landslide": {
#       "required_features": [
#         "rainfall_24h_mm",
#         "rainfall_72h_mm",
#         "slope_degrees"
#       ],
#       "rainfall_24h_threshold_mm": null,
#       "rainfall_72h_threshold_mm": null,
#       "minimum_slope_degrees": null
#     },
#     "slippery_trail": {
#       "required_features": [
#         "rainfall_3h_mm",
#         "rainfall_24h_mm"
#       ],
#       "rainfall_3h_threshold_mm": null,
#       "rainfall_24h_threshold_mm": null
#     },
#     "dense_fog": {
#       "required_features": [
#         "visibility_m"
#       ],
#       "maximum_visibility_m": null
#     },
#     "strong_wind": {
#       "required_features": [
#         "wind_gust_kmh"
#       ],
#       "wind_gust_threshold_kmh": null
#     }
#   }
# }


{
  "metadata": {
    "purpose": "Experimental weather-only hazard indicators",
    "operational_warning_system": false,
    "threshold_status": "PARTIALLY_CONFIGURED - research baseline only; validate before use",
    "notes": [
      "Landslide 24-hour threshold is based on a published Sri Lankan NBRO watch threshold.",
      "72-hour rainfall and slope thresholds require further validation.",
      "Slippery trail and strong wind thresholds remain unset pending suitable evidence.",
      "Fog requires a visibility feature that must be collected before the rule can be evaluated."
    ]
  },
  "rules": {
    "landslide": {
      "required_features": [
        "rainfall_24h_mm",
        "rainfall_72h_mm",
        "slope_degrees"
      ],
      "rainfall_24h_threshold_mm": 75.0,
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
      "maximum_visibility_m": 1000.0
    },
    "strong_wind": {
      "required_features": [
        "wind_gust_kmh"
      ],
      "wind_gust_threshold_kmh": null
    }
  }
}
