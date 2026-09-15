/// TruthLens Analysis and Credibility Assessment Models with Sound Null Safety.

class UserModel {
  final String id;
  final String email;
  final String role;
  final bool isActive;
  final String createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.role,
    required this.isActive,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
      role: json['role']?.toString() ?? 'USER',
      isActive: json['is_active'] as bool? ?? true,
      createdAt: json['created_at']?.toString() ?? '',
    );
  }
}

class AuthTokenResponse {
  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final UserModel user;

  AuthTokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory AuthTokenResponse.fromJson(Map<String, dynamic> json) {
    return AuthTokenResponse(
      accessToken: json['access_token']?.toString() ?? '',
      tokenType: json['token_type']?.toString() ?? 'bearer',
      expiresIn: (json['expires_in'] as num?)?.toInt() ?? 86400,
      user: json['user'] != null
          ? UserModel.fromJson(json['user'] as Map<String, dynamic>)
          : UserModel(
              id: '',
              email: '',
              role: 'USER',
              isActive: true,
              createdAt: '',
            ),
    );
  }
}

class PredictionDetail {
  final String label;
  final double rawScore;
  final double calibratedProbability;
  final int confidence;
  final String confidenceLevel;
  final String modelAgreement;
  final double agreementScore;
  final double oodScore;
  final Map<String, double> modelScores;
  final String summary;
  final String limitations;

  PredictionDetail({
    required this.label,
    required this.rawScore,
    required this.calibratedProbability,
    required this.confidence,
    required this.confidenceLevel,
    required this.modelAgreement,
    required this.agreementScore,
    required this.oodScore,
    required this.modelScores,
    required this.summary,
    required this.limitations,
  });

  factory PredictionDetail.fromJson(Map<String, dynamic> json) {
    final rawScores = json['model_scores'] as Map<String, dynamic>? ?? {};
    final parsedScores = <String, double>{};
    rawScores.forEach((key, value) {
      if (value is num) {
        parsedScores[key] = value.toDouble();
      }
    });

    return PredictionDetail(
      label: json['label']?.toString() ?? 'UNCERTAIN',
      rawScore: (json['raw_score'] as num?)?.toDouble() ?? 0.5,
      calibratedProbability: (json['calibrated_probability'] as num?)?.toDouble() ?? 0.5,
      confidence: (json['confidence'] as num?)?.round() ?? 50,
      confidenceLevel: json['confidence_level']?.toString() ?? 'Medium',
      modelAgreement: json['model_agreement']?.toString() ?? 'Medium',
      agreementScore: (json['agreement_score'] as num?)?.toDouble() ?? 0.5,
      oodScore: (json['ood_score'] as num?)?.toDouble() ?? 0.0,
      modelScores: parsedScores,
      summary: json['summary']?.toString() ?? 'Analysis completed.',
      limitations: json['limitations']?.toString() ?? 'Calibrated probabilistic assessment.',
    );
  }
}

class ClaimItem {
  final String claimId;
  final String text;
  final int sentenceIndex;
  final String claimType;
  final double confidence;
  final String verificationPriority;
  final List<String> keywords;

  ClaimItem({
    required this.claimId,
    required this.text,
    required this.sentenceIndex,
    required this.claimType,
    required this.confidence,
    required this.verificationPriority,
    required this.keywords,
  });

  factory ClaimItem.fromJson(Map<String, dynamic> json) {
    final rawKw = json['keywords'] as List<dynamic>? ?? [];
    return ClaimItem(
      claimId: json['claim_id']?.toString() ?? '',
      text: json['text']?.toString() ?? '',
      sentenceIndex: (json['sentence_index'] as num?)?.toInt() ?? 0,
      claimType: json['claim_type']?.toString() ?? 'factual',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.5,
      verificationPriority: json['verification_priority']?.toString() ?? 'Medium',
      keywords: rawKw.map((e) => e.toString()).toList(),
    );
  }
}

class EvidenceItem {
  final String sourceName;
  final String? url;
  final String title;
  final String? publisher;
  final String retrievedAt;
  final double relevanceScore;
  final String evidenceType;
  final String summary;

  EvidenceItem({
    required this.sourceName,
    this.url,
    required this.title,
    this.publisher,
    required this.retrievedAt,
    required this.relevanceScore,
    required this.evidenceType,
    required this.summary,
  });

  factory EvidenceItem.fromJson(Map<String, dynamic> json) {
    return EvidenceItem(
      sourceName: json['source_name']?.toString() ?? 'Public Database',
      url: json['url']?.toString(),
      title: json['title']?.toString() ?? 'Reference Evidence',
      publisher: json['publisher']?.toString(),
      retrievedAt: json['retrieved_at']?.toString() ?? '',
      relevanceScore: (json['relevance_score'] as num?)?.toDouble() ?? 0.8,
      evidenceType: json['evidence_type']?.toString() ?? 'contextual',
      summary: json['summary']?.toString() ?? '',
    );
  }
}

class HighlightSpan {
  final String text;
  final int startChar;
  final int endChar;
  final String influenceLevel;
  final String direction;
  final double weight;
  final String explanation;

  HighlightSpan({
    required this.text,
    required this.startChar,
    required this.endChar,
    required this.influenceLevel,
    required this.direction,
    required this.weight,
    required this.explanation,
  });

  factory HighlightSpan.fromJson(Map<String, dynamic> json) {
    return HighlightSpan(
      text: json['text']?.toString() ?? '',
      startChar: (json['start_char'] as num?)?.toInt() ?? 0,
      endChar: (json['end_char'] as num?)?.toInt() ?? 0,
      influenceLevel: json['influence_level']?.toString() ?? 'medium',
      direction: json['direction']?.toString() ?? 'supports_credible',
      weight: (json['weight'] as num?)?.toDouble() ?? 0.1,
      explanation: json['explanation']?.toString() ?? '',
    );
  }
}

class ExplanationDetail {
  final List<List<dynamic>> supportingSignals;
  final List<List<dynamic>> counterSignals;
  final List<dynamic> structuralDeviations;
  final List<HighlightSpan> highlightedSpans;

  ExplanationDetail({
    required this.supportingSignals,
    required this.counterSignals,
    required this.structuralDeviations,
    required this.highlightedSpans,
  });

  factory ExplanationDetail.fromJson(Map<String, dynamic> json) {
    final rawSup = json['supporting_signals'] as List<dynamic>? ?? [];
    final rawCou = json['counter_signals'] as List<dynamic>? ?? [];
    final rawDev = json['structural_deviations'] as List<dynamic>? ?? [];
    final rawSpans = json['highlighted_spans'] as List<dynamic>? ?? [];

    return ExplanationDetail(
      supportingSignals: rawSup.map((e) => (e is List) ? e.toList() : [e.toString(), 0.0]).toList(),
      counterSignals: rawCou.map((e) => (e is List) ? e.toList() : [e.toString(), 0.0]).toList(),
      structuralDeviations: rawDev,
      highlightedSpans: rawSpans
          .whereType<Map<String, dynamic>>()
          .map((s) => HighlightSpan.fromJson(s))
          .toList(),
    );
  }
}

class AnalysisResponse {
  final String id;
  final String title;
  final String inputType;
  final String? sourceUrl;
  final String language;
  final String status;
  final String createdAt;
  final PredictionDetail? prediction;
  final List<ClaimItem> claims;
  final List<EvidenceItem> evidence;
  final ExplanationDetail? explanation;

  AnalysisResponse({
    required this.id,
    required this.title,
    required this.inputType,
    this.sourceUrl,
    required this.language,
    required this.status,
    required this.createdAt,
    this.prediction,
    required this.claims,
    required this.evidence,
    this.explanation,
  });

  factory AnalysisResponse.fromJson(Map<String, dynamic> json) {
    final rawClaims = json['claims'] as List<dynamic>? ?? [];
    final rawEvidence = json['evidence'] as List<dynamic>? ?? [];

    return AnalysisResponse(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Credibility Assessment',
      inputType: json['input_type']?.toString() ?? 'article',
      sourceUrl: json['source_url']?.toString(),
      language: json['language']?.toString() ?? 'en',
      status: json['status']?.toString() ?? 'COMPLETED',
      createdAt: json['created_at']?.toString() ?? '',
      prediction: json['prediction'] != null
          ? PredictionDetail.fromJson(json['prediction'] as Map<String, dynamic>)
          : null,
      claims: rawClaims
          .whereType<Map<String, dynamic>>()
          .map((c) => ClaimItem.fromJson(c))
          .toList(),
      evidence: rawEvidence
          .whereType<Map<String, dynamic>>()
          .map((e) => EvidenceItem.fromJson(e))
          .toList(),
      explanation: json['explanation'] != null
          ? ExplanationDetail.fromJson(json['explanation'] as Map<String, dynamic>)
          : null,
    );
  }
}

class AnalysisListItem {
  final String id;
  final String title;
  final String inputType;
  final String? sourceUrl;
  final String status;
  final String createdAt;
  final String? label;
  final int? confidence;
  final double? calibratedProbability;

  AnalysisListItem({
    required this.id,
    required this.title,
    required this.inputType,
    this.sourceUrl,
    required this.status,
    required this.createdAt,
    this.label,
    this.confidence,
    this.calibratedProbability,
  });

  factory AnalysisListItem.fromJson(Map<String, dynamic> json) {
    return AnalysisListItem(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Untitled Analysis',
      inputType: json['input_type']?.toString() ?? 'article',
      sourceUrl: json['source_url']?.toString(),
      status: json['status']?.toString() ?? 'COMPLETED',
      createdAt: json['created_at']?.toString() ?? '',
      label: json['label']?.toString(),
      confidence: (json['confidence'] as num?)?.round(),
      calibratedProbability: (json['calibrated_probability'] as num?)?.toDouble(),
    );
  }
}
