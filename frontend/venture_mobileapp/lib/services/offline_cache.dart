import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class CachedJson {
  const CachedJson({required this.data, required this.updatedAt});

  final Map<String, dynamic> data;
  final DateTime updatedAt;
}

class OfflineCache {
  static const _keyPrefix = 'venture.cache.';

  Future<void> save(String key, Map<String, dynamic> data) async {
    final preferences = await SharedPreferences.getInstance();
    final envelope = {
      'data': data,
      'updated_at': DateTime.now().toUtc().toIso8601String(),
    };
    final saved = await preferences.setString(
      '$_keyPrefix$key',
      jsonEncode(envelope),
    );
    if (!saved) throw StateError('Could not save the offline copy.');
  }

  Future<CachedJson?> read(String key) async {
    final preferences = await SharedPreferences.getInstance();
    final encoded = preferences.getString('$_keyPrefix$key');
    if (encoded == null) return null;

    final envelope = jsonDecode(encoded);
    if (envelope is! Map<String, dynamic> ||
        envelope['data'] is! Map<String, dynamic> ||
        envelope['updated_at'] is! String) {
      throw const FormatException('The saved offline copy is invalid.');
    }

    return CachedJson(
      data: envelope['data'] as Map<String, dynamic>,
      updatedAt: DateTime.parse(envelope['updated_at'] as String).toLocal(),
    );
  }
}
