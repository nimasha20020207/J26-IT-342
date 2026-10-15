class HazardItem {
  final String name;
  final double probability; // 0.0 to 1.0
  final String severity;    // Low, Medium, High

  HazardItem({required this.name, required this.probability, required this.severity});
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
}