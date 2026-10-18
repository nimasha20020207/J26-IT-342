
# {
#   "metadata": {
#     "purpose": "Experimental weather-only hazard indicators",
#     "operational_warning_system": false,
#     "threshold_status": "PARTIALLY_CONFIGURED - research baseline only; validate before use",
#     "notes": [
#       "Landslide 24-hour threshold is based on a published Sri Lankan NBRO watch threshold.",
#       "72-hour rainfall and slope thresholds require further validation.",
#       "Slippery trail and strong wind thresholds remain unset pending suitable evidence.",
#       "Fog requires a visibility feature that must be collected before the rule can be evaluated."
#     ]
#   },
#   "rules": {
#     "landslide": {
#       "required_features": [
#         "rainfall_24h_mm",
#         "rainfall_72h_mm",
#         "slope_degrees"
#       ],
#       "rainfall_24h_threshold_mm": 75.0,
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
#       "maximum_visibility_m": 1000.0
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
    "purpose": "Experimental weather-based hiking hazard indicators",
    "operational_warning_system": false,
    "threshold_status": "PROVISIONAL_DEMONSTRATION_VALUES",
    "notes": [
      "Thresholds marked provisional must be validated before operational use.",
      "Rainfall is used as an environmental indicator for landslide and rockfall susceptibility, not confirmation of an event.",
      "Humidity and dew-point depression estimate fog-favourable conditions, not measured visibility.",
      "Rainfall and humidity are candidate indicators for leech activity, not confirmed leech presence.",
      "Strong winds are used as a proxy for possible trail obstructions, not confirmation of a blockage."
    ]
  },
  "rules": {
    "landslide": {
      "enabled": true,
      "indicator_type": "RAIN_GAUGE_THRESHOLD",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "all",
      "conditions": [
        {
          "feature": "rainfall_24h_mm",
          "operator": ">=",
          "threshold": 75.0
        }
      ]
    },
    "rockfall": {
      "enabled": true,
      "indicator_type": "RAINFALL_SUSCEPTIBILITY_PROXY",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "all",
      "conditions": [
        {
          "feature": "rainfall_24h_mm",
          "operator": ">=",
          "threshold": 75.0
        }
      ]
    },
    "slippery_trail": {
      "enabled": true,
      "indicator_type": "WET_TRAIL_PROXY",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "any",
      "conditions": [
        {
          "feature": "rainfall_3h_mm",
          "operator": ">=",
          "threshold": 10.0
        },
        {
          "feature": "rainfall_24h_mm",
          "operator": ">=",
          "threshold": 25.0
        }
      ]
    },
    "dense_fog": {
      "enabled": true,
      "indicator_type": "FOG_FAVOURABLE_CONDITIONS",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "all",
      "conditions": [
        {
          "feature": "relative_humidity_pct",
          "operator": ">=",
          "threshold": 95.0
        },
        {
          "feature": "dew_point_depression_c",
          "operator": "<=",
          "threshold": 2.0
        }
      ]
    },
    "leech_activity": {
      "enabled": true,
      "indicator_type": "WET_HUMID_CONDITIONS",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "all",
      "conditions": [
        {
          "feature": "rainfall_24h_mm",
          "operator": ">=",
          "threshold": 10.0
        },
        {
          "feature": "relative_humidity_pct",
          "operator": ">=",
          "threshold": 85.0
        }
      ]
    },
    "heavy_rain": {
      "enabled": true,
      "indicator_type": "RAINFALL_THRESHOLD",
      "evidence_level": "ENVIRONMENTAL_INDICATOR",
      "logic": "all",
      "conditions": [
        {
          "feature": "rainfall_24h_mm",
          "operator": ">=",
          "threshold": 50.0
        }
      ]
    },
    "strong_wind": {
      "enabled": true,
      "indicator_type": "WIND_GUST_THRESHOLD",
      "evidence_level": "ENVIRONMENTAL_INDICATOR",
      "logic": "all",
      "conditions": [
        {
          "feature": "wind_gust_kmh",
          "operator": ">=",
          "threshold": 40.0
        }
      ]
    },
    "trail_obstruction": {
      "enabled": true,
      "indicator_type": "WIND_RELATED_OBSTRUCTION_PROXY",
      "evidence_level": "ENVIRONMENTAL_PROXY",
      "logic": "all",
      "conditions": [
        {
          "feature": "wind_gust_kmh",
          "operator": ">=",
          "threshold": 50.0
        }
      ]
    }
  }
}
