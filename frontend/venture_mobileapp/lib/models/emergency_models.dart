// Dart Models for Component 4: Context-Aware Emergency Detection & Response Recommendation

class IncidentInputModel {
  final String incidentText;
  final double latitude;
  final double longitude;
  final String trailName;
  final double elevationM;
  final double slopeDegrees;
  final double rainfallMm;
  final double temperatureC;
  final double windSpeedKmh;
  final double visibilityPct;
  final double hoursHiking;
  final double distanceFromTrailheadKm;
  final double phoneBatteryPct;
  final int fatigueScore1to10;
  final double waterRemainingL;
  final int remoteArea;
  final String terrainType;

  IncidentInputModel({
    required this.incidentText,
    this.latitude = 6.8096,
    this.longitude = 80.8028,
    this.trailName = 'Horton_Plains',
    this.elevationM = 2100.0,
    this.slopeDegrees = 25.0,
    this.rainfallMm = 35.0,
    this.temperatureC = 17.0,
    this.windSpeedKmh = 18.0,
    this.visibilityPct = 30.0,
    this.hoursHiking = 4.5,
    this.distanceFromTrailheadKm = 5.2,
    this.phoneBatteryPct = 25.0,
    this.fatigueScore1to10 = 7,
    this.waterRemainingL = 0.5,
    this.remoteArea = 1,
    this.terrainType = 'rocky',
  });

  Map<String, dynamic> toJson() => {
    'incident_text': incidentText,
    'latitude': latitude,
    'longitude': longitude,
    'trail_name': trailName,
    'elevation_m': elevationM,
    'slope_degrees': slopeDegrees,
    'rainfall_mm': rainfallMm,
    'temperature_c': temperatureC,
    'wind_speed_kmh': windSpeedKmh,
    'visibility_pct': visibilityPct,
    'hours_hiking': hoursHiking,
    'distance_from_trailhead_km': distanceFromTrailheadKm,
    'phone_battery_pct': phoneBatteryPct,
    'fatigue_score_1_10': fatigueScore1to10,
    'water_remaining_l': waterRemainingL,
    'remote_area': remoteArea,
    'terrain_type': terrainType,
  };
}

class EmergencyAssessmentModel {
  final String emergencyType;
  final String displayTitle;
  final int severityLevel;
  final String urgency;
  final double confidencePct;
  final bool requiresRescue;
  final String structuredPrediction;
  final String nlpPrediction;

  EmergencyAssessmentModel({
    required this.emergencyType,
    required this.displayTitle,
    required this.severityLevel,
    required this.urgency,
    required this.confidencePct,
    required this.requiresRescue,
    required this.structuredPrediction,
    required this.nlpPrediction,
  });

  factory EmergencyAssessmentModel.fromJson(Map<String, dynamic> json) => EmergencyAssessmentModel(
    emergencyType: json['emergency_type'] ?? 'injury',
    displayTitle: json['display_title'] ?? 'Emergency Incident',
    severityLevel: (json['severity_level'] as num?)?.toInt() ?? 3,
    urgency: json['urgency'] ?? 'MODERATE',
    confidencePct: (json['confidence_pct'] as num?)?.toDouble() ?? 90.0,
    requiresRescue: json['requires_rescue'] ?? true,
    structuredPrediction: json['structured_prediction'] ?? '',
    nlpPrediction: json['nlp_prediction'] ?? '',
  );
}

class RecommendedActionModel {
  final String actionId;
  final String title;
  final String priority;
  final String urgency;
  final int effectivenessPct;
  final String? reasoningPath;
  final bool isPrimary;

  RecommendedActionModel({
    required this.actionId,
    required this.title,
    required this.priority,
    required this.urgency,
    required this.effectivenessPct,
    this.reasoningPath,
    this.isPrimary = false,
  });

  factory RecommendedActionModel.fromJson(Map<String, dynamic> json) => RecommendedActionModel(
    actionId: json['action_id'] ?? '',
    title: json['title'] ?? '',
    priority: json['priority'] ?? 'Priority: Medium',
    urgency: json['urgency'] ?? 'Urgency: Urgent',
    effectivenessPct: (json['effectiveness_pct'] as num?)?.toInt() ?? 85,
    reasoningPath: json['reasoning_path'],
    isPrimary: json['is_primary'] ?? false,
  );
}

class NearestResourceModel {
  final String id;
  final String name;
  final String type;
  final double distanceKm;
  final String distanceStr;
  final int estimatedTimeMins;
  final String estimatedTimeStr;
  final String phone;
  final double latitude;
  final double longitude;
  final List<String> services;

  NearestResourceModel({
    required this.id,
    required this.name,
    required this.type,
    required this.distanceKm,
    required this.distanceStr,
    required this.estimatedTimeMins,
    required this.estimatedTimeStr,
    required this.phone,
    required this.latitude,
    required this.longitude,
    required this.services,
  });

  factory NearestResourceModel.fromJson(Map<String, dynamic> json) => NearestResourceModel(
    id: json['id'] ?? '',
    name: json['name'] ?? '',
    type: json['type'] ?? 'Emergency Unit',
    distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
    distanceStr: json['distance_str'] ?? '0.0 km',
    estimatedTimeMins: (json['estimated_time_mins'] as num?)?.toInt() ?? 10,
    estimatedTimeStr: json['estimated_time_str'] ?? '10 mins',
    phone: json['phone'] ?? '+94 119',
    latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
    longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
    services: (json['services'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
  );
}

class XAIFactorModel {
  final String factor;
  final double impactPercentage;

  XAIFactorModel({required this.factor, required this.impactPercentage});

  factory XAIFactorModel.fromJson(Map<String, dynamic> json) => XAIFactorModel(
    factor: json['factor'] ?? '',
    impactPercentage: (json['impact_percentage'] as num?)?.toDouble() ?? 0.0,
  );
}

class XAIExplanationModel {
  final List<XAIFactorModel> topContributingFactors;
  final List<String> explanatoryNarrative;
  final String modelType;
  final String interpretabilityFramework;

  XAIExplanationModel({
    required this.topContributingFactors,
    required this.explanatoryNarrative,
    required this.modelType,
    required this.interpretabilityFramework,
  });

  factory XAIExplanationModel.fromJson(Map<String, dynamic> json) => XAIExplanationModel(
    topContributingFactors: (json['top_contributing_factors'] as List<dynamic>?)
        ?.map((e) => XAIFactorModel.fromJson(e))
        .toList() ?? [],
    explanatoryNarrative: (json['explanatory_narrative'] as List<dynamic>?)
        ?.map((e) => e.toString())
        .toList() ?? [],
    modelType: json['model_type'] ?? 'SHAP',
    interpretabilityFramework: json['interpretability_framework'] ?? 'SHAP TreeExplainer',
  );
}

class ContextSummaryModel {
  final String? trailName;
  final String coordinates;
  final String weather;
  final String terrain;
  final String hikerStatus;
  final bool remoteArea;

  ContextSummaryModel({
    this.trailName,
    required this.coordinates,
    required this.weather,
    required this.terrain,
    required this.hikerStatus,
    required this.remoteArea,
  });

  factory ContextSummaryModel.fromJson(Map<String, dynamic> json) => ContextSummaryModel(
    trailName: json['trail_name'],
    coordinates: json['coordinates'] ?? '',
    weather: json['weather'] ?? '',
    terrain: json['terrain'] ?? '',
    hikerStatus: json['hiker_status'] ?? '',
    remoteArea: json['remote_area'] ?? false,
  );
}

class FullEmergencyResponseModel {
  final bool success;
  final String timestamp;
  final EmergencyAssessmentModel assessment;
  final List<RecommendedActionModel> recommendedActions;
  final List<String> reasoningPaths;
  final List<String> activeHazards;
  final List<NearestResourceModel> nearestResources;
  final XAIExplanationModel explainability;
  final ContextSummaryModel contextSummary;

  FullEmergencyResponseModel({
    required this.success,
    required this.timestamp,
    required this.assessment,
    required this.recommendedActions,
    required this.reasoningPaths,
    required this.activeHazards,
    required this.nearestResources,
    required this.explainability,
    required this.contextSummary,
  });

  factory FullEmergencyResponseModel.fromJson(Map<String, dynamic> json) => FullEmergencyResponseModel(
    success: json['success'] ?? true,
    timestamp: json['timestamp'] ?? '',
    assessment: EmergencyAssessmentModel.fromJson(json['assessment'] ?? {}),
    recommendedActions: (json['recommended_actions'] as List<dynamic>?)
        ?.map((e) => RecommendedActionModel.fromJson(e))
        .toList() ?? [],
    reasoningPaths: (json['reasoning_paths'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
    activeHazards: (json['active_hazards'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
    nearestResources: (json['nearest_resources'] as List<dynamic>?)
        ?.map((e) => NearestResourceModel.fromJson(e))
        .toList() ?? [],
    explainability: XAIExplanationModel.fromJson(json['explainability'] ?? {}),
    contextSummary: ContextSummaryModel.fromJson(json['context_summary'] ?? {}),
  );
}
