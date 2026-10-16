class HazardItem {
  final String name;
  final double probability; // 0.0 to 1.0
  final String severity;    // Low, Medium, High

  HazardItem({required this.name, required this.probability, required this.severity});

  factory HazardItem.fromJson(Map<String, dynamic> json) => HazardItem(
        name: json['name'] as String,
        probability: (json['probability'] as num).toDouble(),
        severity: json['severity'] as String,
      );
}

class SocialReport {
  final String source;
  final String type; // 'News' or 'Hiker Review'
  final String content;
  final String timeAgo;
  final double reliabilityScore; // e.g. 0.92
  final String confidenceIndicator; // High, Moderate

  SocialReport({
    required this.source,
    required this.type,
    required this.content,
    required this.timeAgo,
    required this.reliabilityScore,
    required this.confidenceIndicator,
  });

  factory SocialReport.fromJson(Map<String, dynamic> json) => SocialReport(
        source: json['source'] as String,
        type: json['type'] as String,
        content: json['content'] as String,
        timeAgo: json['time_ago'] as String,
        reliabilityScore: (json['reliability_score'] as num).toDouble(),
        confidenceIndicator: json['confidence_indicator'] as String,
      );
}

class WeatherSummary {
  final DateTime forecastDate;
  final String source;
  final double temperatureC;
  final double feelsLikeC;
  final String condition;
  final int rainChance;
  final double precipitationMm;
  final double windSpeedKmh;
  final double windGustKmh;
  final int humidity;

  const WeatherSummary({
    required this.forecastDate,
    required this.source,
    required this.temperatureC,
    required this.feelsLikeC,
    required this.condition,
    required this.rainChance,
    required this.precipitationMm,
    required this.windSpeedKmh,
    required this.windGustKmh,
    required this.humidity,
  });

  factory WeatherSummary.fromJson(Map<String, dynamic> json) => WeatherSummary(
        forecastDate: DateTime.parse(json['forecast_date'] as String),
        source: json['source'] as String,
        temperatureC: (json['temperature_c'] as num).toDouble(),
        feelsLikeC: (json['feels_like_c'] as num).toDouble(),
        condition: json['condition'] as String,
        rainChance: (json['rain_chance'] as num).toInt(),
        precipitationMm: (json['precipitation_mm'] as num).toDouble(),
        windSpeedKmh: (json['wind_speed_kmh'] as num).toDouble(),
        windGustKmh: (json['wind_gust_kmh'] as num).toDouble(),
        humidity: (json['humidity'] as num).toInt(),
      );
}

class RiskTrend {
  final String time;
  final String risk;
  final int score;

  const RiskTrend({required this.time, required this.risk, required this.score});

  factory RiskTrend.fromJson(Map<String, dynamic> json) => RiskTrend(
        time: json['time'] as String,
        risk: json['risk'] as String,
        score: json['score'] as int,
      );
}

class DailyPrediction {
  final DateTime date;
  final int riskScore;
  final String riskLevel;

  const DailyPrediction({required this.date, required this.riskScore, required this.riskLevel});

  factory DailyPrediction.fromJson(Map<String, dynamic> json) => DailyPrediction(
        date: DateTime.parse(json['date'] as String),
        riskScore: json['risk_score'] as int,
        riskLevel: json['risk_level'] as String,
      );
}

class ForecastData {
  final String requestId;
  final String mode;
  final String trailName;
  final DateTime startDate;
  final DateTime endDate;
  final int overallRiskScore;
  final String riskLevel;
  final List<HazardItem> hazards;
  final WeatherSummary weather;
  final String recommendationAction;
  final String recommendationSummary;
  final List<String> precautions;
  final List<SocialReport> socialReports;
  final List<RiskTrend> hourlyTrends;
  final List<DailyPrediction> dailyPredictions;

  const ForecastData({
    required this.requestId,
    required this.mode,
    required this.trailName,
    required this.startDate,
    required this.endDate,
    required this.overallRiskScore,
    required this.riskLevel,
    required this.hazards,
    required this.weather,
    required this.recommendationAction,
    required this.recommendationSummary,
    required this.precautions,
    required this.socialReports,
    required this.hourlyTrends,
    required this.dailyPredictions,
  });

  factory ForecastData.fromJson(Map<String, dynamic> json) {
    final recommendation = json['recommendation'] as Map<String, dynamic>;

    return ForecastData(
      requestId: json['request_id'] as String,
      mode: json['mode'] as String,
      trailName: json['trail_name'] as String,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      overallRiskScore: json['overall_risk_score'] as int,
      riskLevel: json['risk_level'] as String,
      hazards: (json['hazards'] as List<dynamic>)
          .map((item) => HazardItem.fromJson(item as Map<String, dynamic>))
          .toList(),
      weather: WeatherSummary.fromJson(json['weather'] as Map<String, dynamic>),
      recommendationAction: recommendation['action'] as String,
      recommendationSummary: recommendation['summary'] as String,
      precautions: (recommendation['precautions'] as List<dynamic>).cast<String>(),
      socialReports: (json['social_reports'] as List<dynamic>)
          .map((item) => SocialReport.fromJson(item as Map<String, dynamic>))
          .toList(),
      hourlyTrends: (json['hourly_trends'] as List<dynamic>)
          .map((item) => RiskTrend.fromJson(item as Map<String, dynamic>))
          .toList(),
      dailyPredictions: (json['daily_predictions'] as List<dynamic>)
          .map((item) => DailyPrediction.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}