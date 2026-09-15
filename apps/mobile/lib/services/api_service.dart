import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/analysis_model.dart';

class ApiException implements Exception {
  final String message;
  final String? code;
  final int? statusCode;

  ApiException(this.message, {this.code, this.statusCode});

  @override
  String toString() => message;
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  /// Optional override for testing on physical devices or custom IP endpoints
  static String? customBaseUrl;

  /// Determine backend URL based on platform and optional override
  String get baseUrl {
    if (customBaseUrl != null && customBaseUrl!.isNotEmpty) {
      return customBaseUrl!;
    }
    if (kIsWeb) {
      return 'http://127.0.0.1:8000/api/v1';
    }
    try {
      if (Platform.isAndroid) {
        // Android Emulator maps host machine localhost to 10.0.2.2
        return 'http://10.0.2.2:8000/api/v1';
      }
    } catch (_) {}
    return 'http://127.0.0.1:8000/api/v1';
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('truthlens_token');
  }

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('truthlens_token', token);
  }

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('truthlens_token');
  }

  Future<Map<String, String>> _headers() async {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    final token = await getToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<dynamic> _request(
    String endpoint, {
    String method = 'GET',
    dynamic body,
  }) async {
    final uri = Uri.parse('$baseUrl$endpoint');
    final headers = await _headers();

    http.Response response;
    try {
      if (method == 'POST') {
        response = await http
            .post(uri, headers: headers, body: jsonEncode(body))
            .timeout(const Duration(seconds: 15));
      } else if (method == 'DELETE') {
        response = await http
            .delete(uri, headers: headers)
            .timeout(const Duration(seconds: 15));
      } else {
        response = await http
            .get(uri, headers: headers)
            .timeout(const Duration(seconds: 15));
      }
    } on TimeoutException {
      throw ApiException('Connection timed out. Please check your network connection.');
    } catch (e) {
      throw ApiException('Could not connect to TruthLens backend: $e');
    }

    Map<String, dynamic> jsonBody;
    try {
      jsonBody = jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException(
        'Server returned invalid response (HTTP ${response.statusCode})',
        statusCode: response.statusCode,
      );
    }

    if (response.statusCode == 401) {
      await clearToken();
    }

    final success = jsonBody['success'] as bool? ?? false;
    if (!success || response.statusCode >= 400) {
      String msg = 'An error occurred.';
      String? code;

      if (jsonBody['error'] is Map) {
        final err = jsonBody['error'] as Map<String, dynamic>;
        msg = err['message']?.toString() ?? msg;
        code = err['code']?.toString();
      } else if (jsonBody['error'] is String) {
        msg = jsonBody['error'] as String;
      } else if (jsonBody['detail'] != null) {
        final detail = jsonBody['detail'];
        if (detail is List && detail.isNotEmpty) {
          final first = detail.first;
          if (first is Map && first.containsKey('msg')) {
            msg = first['msg'].toString();
          } else {
            msg = detail.toString();
          }
        } else {
          msg = detail.toString();
        }
      } else if (jsonBody['message'] != null) {
        msg = jsonBody['message'].toString();
      }

      throw ApiException(msg, code: code, statusCode: response.statusCode);
    }

    return jsonBody['data'];
  }

  // --- Authentication ---

  /// Log in with email and password
  Future<AuthTokenResponse> login(String email, String password) async {
    final data = await _request('/auth/login', method: 'POST', body: {
      'email': email,
      'password': password,
    });
    final tokenResp = AuthTokenResponse.fromJson(data as Map<String, dynamic>);
    await saveToken(tokenResp.accessToken);
    return tokenResp;
  }

  /// Register a new user account
  Future<AuthTokenResponse> register(String email, String password) async {
    final data = await _request('/auth/register', method: 'POST', body: {
      'email': email,
      'password': password,
    });
    final tokenResp = AuthTokenResponse.fromJson(data as Map<String, dynamic>);
    await saveToken(tokenResp.accessToken);
    return tokenResp;
  }

  /// Get current user profile
  Future<UserModel> getMe() async {
    final data = await _request('/auth/me');
    return UserModel.fromJson(data as Map<String, dynamic>);
  }

  /// Log out from session
  Future<void> logout() async {
    try {
      await _request('/auth/logout', method: 'POST');
    } catch (_) {}
    await clearToken();
  }

  // --- Analysis Operations ---

  /// Analyze text (article or headline)
  Future<AnalysisResponse> analyzeText({
    required String text,
    String? headline,
    String inputType = 'article',
  }) async {
    final data = await _request('/analysis', method: 'POST', body: {
      'text': text,
      if (headline != null && headline.isNotEmpty) 'headline': headline,
      'input_type': inputType,
    });
    return AnalysisResponse.fromJson(data as Map<String, dynamic>);
  }

  /// Analyze URL safely with backend SSRF verification
  Future<AnalysisResponse> analyzeUrl(String url) async {
    final data = await _request('/analysis/url', method: 'POST', body: {
      'url': url,
    });
    return AnalysisResponse.fromJson(data as Map<String, dynamic>);
  }

  /// Get analysis by ID
  Future<AnalysisResponse> getAnalysis(String id) async {
    final data = await _request('/analysis/$id');
    return AnalysisResponse.fromJson(data as Map<String, dynamic>);
  }

  /// List historical analyses
  Future<List<AnalysisListItem>> listAnalyses({
    String? search,
    String? assessment,
    String? inputType,
  }) async {
    final queryParams = <String, String>{};
    if (search != null && search.isNotEmpty) queryParams['search'] = search;
    if (assessment != null && assessment.isNotEmpty) queryParams['assessment'] = assessment;
    if (inputType != null && inputType.isNotEmpty) queryParams['input_type'] = inputType;

    final qs = queryParams.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&');
    final endpoint = '/analysis${qs.isNotEmpty ? '?$qs' : ''}';

    final data = await _request(endpoint);
    final list = data as List<dynamic>? ?? [];
    return list
        .whereType<Map<String, dynamic>>()
        .map((item) => AnalysisListItem.fromJson(item))
        .toList();
  }

  /// Delete analysis
  Future<void> deleteAnalysis(String id) async {
    await _request('/analysis/$id', method: 'DELETE');
  }

  /// Submit feedback
  Future<void> submitFeedback(String id, bool isUseful, {String? comment}) async {
    await _request('/analysis/$id/feedback', method: 'POST', body: {
      'is_useful': isUseful,
      if (comment != null && comment.isNotEmpty) 'comment': comment,
    });
  }

  /// Get model registry
  Future<List<Map<String, dynamic>>> getModels() async {
    final data = await _request('/models');
    final list = data as List<dynamic>? ?? [];
    return list.whereType<Map<String, dynamic>>().toList();
  }
}
