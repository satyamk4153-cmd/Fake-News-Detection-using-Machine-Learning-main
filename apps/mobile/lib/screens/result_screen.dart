import 'package:flutter/material.dart';
import '../models/analysis_model.dart';
import '../widgets/credibility_gauge.dart';
import '../services/api_service.dart';

class ResultScreen extends StatefulWidget {
  final AnalysisResponse analysis;

  const ResultScreen({super.key, required this.analysis});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _feedbackSent = false;

  Future<void> _submitFeedback(bool isUseful) async {
    try {
      await ApiService().submitFeedback(widget.analysis.id, isUseful);
      if (!mounted) return;
      setState(() {
        _feedbackSent = true;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Feedback submitted. Thank you!')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Feedback submission failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final pred = widget.analysis.prediction;
    final expl = widget.analysis.explanation;
    final claims = widget.analysis.claims;
    final evidence = widget.analysis.evidence;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Credibility Assessment', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Primary Credibility Gauge
              if (pred != null)
                CredibilityGauge(
                  probability: pred.calibratedProbability,
                  label: pred.label,
                  confidence: pred.confidence,
                  modelAgreement: pred.modelAgreement,
                ),

              const SizedBox(height: 16),

              // Title and Summary Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.analysis.title,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    if (pred != null)
                      Text(
                        pred.summary,
                        style: TextStyle(fontSize: 13, color: Colors.grey.shade700, height: 1.4),
                      ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Multi-Model Probabilities
              if (pred != null && pred.modelScores.isNotEmpty) ...[
                const Text(
                  'Constituent Model Breakdown',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...pred.modelScores.entries.map((entry) {
                  final pct = (entry.value * 100).toStringAsFixed(1);
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _formatModelName(entry.key),
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                        ),
                        Text(
                          '$pct%',
                          style: const TextStyle(
                            fontSize: 13,
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 20),
              ],

              // Influential Linguistic Signals
              if (expl != null && (expl.supportingSignals.isNotEmpty || expl.counterSignals.isNotEmpty)) ...[
                const Text(
                  'Influential Linguistic Signals',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                if (expl.supportingSignals.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.green.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'SIGNALS SUPPORTING CREDIBILITY',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.green.shade900),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: expl.supportingSignals.map((item) {
                            final term = item.isNotEmpty ? item[0].toString() : '';
                            final weight = item.length > 1 ? item[1].toString() : '';
                            return Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.green.shade300),
                              ),
                              child: Text(
                                '"$term" +$weight',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.green.shade900),
                              ),
                            );
                          }).toList(),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
                if (expl.counterSignals.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'SIGNALS SUPPORTING MISLEADING SCORE',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.red.shade900),
                        ),
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: expl.counterSignals.map((item) {
                            final term = item.isNotEmpty ? item[0].toString() : '';
                            final weight = item.length > 1 ? item[1].toString() : '';
                            return Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.red.shade300),
                              ),
                              child: Text(
                                '"$term" -$weight',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.red.shade900),
                              ),
                            );
                          }).toList(),
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 20),
              ],

              // Extracted Verifiable Claims
              if (claims.isNotEmpty) ...[
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Extracted Verifiable Claims',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      '${claims.length} claims',
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ...claims.map((claim) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade200,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                claim.claimType.toUpperCase(),
                                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                            Text(
                              'Priority: ${claim.verificationPriority}',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: claim.verificationPriority == 'High'
                                    ? Colors.amber.shade800
                                    : Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(
                          claim.text,
                          style: const TextStyle(fontSize: 13, height: 1.3),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 20),
              ],

              // Attributed Reference Evidence
              if (evidence.isNotEmpty) ...[
                const Text(
                  'Attributed Reference Evidence',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...evidence.map((ev) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Text(
                                ev.title,
                                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                              ),
                            ),
                            if (ev.url != null && ev.url!.isNotEmpty)
                              const Icon(Icons.open_in_new, size: 16, color: Colors.grey),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          ev.summary,
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade700, height: 1.3),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Source: ${ev.sourceName}',
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                        ),
                      ],
                    ),
                  );
                }),
                const SizedBox(height: 20),
              ] else ...[
                // Honest fallback when no external evidence is indexed
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.info_outline, size: 16, color: Colors.grey.shade600),
                          const SizedBox(width: 8),
                          Text(
                            'External Knowledge Base Attribution',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: Colors.grey.shade800,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'No direct encyclopedic citations or public fact-check records were indexed for the specific entities in this submission. TruthLens strictly does not fabricate mock citations when verified external records are unavailable. Users should independently cross-verify these claims against primary journalistic and institutional archives.',
                        style: TextStyle(fontSize: 11, color: Colors.grey.shade600, height: 1.3),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],

              // Limitations Card
              if (pred != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.info_outline, size: 18, color: Colors.grey.shade600),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          pred.limitations,
                          style: TextStyle(fontSize: 11, color: Colors.grey.shade700, height: 1.3),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],

              // Feedback Widget
              if (!_feedbackSent)
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade300),
                  ),
                  child: Row(
                    children: [
                      const Expanded(
                        child: Text(
                          'Was this assessment helpful?',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                      ),
                      IconButton(
                        onPressed: () => _submitFeedback(true),
                        icon: const Icon(Icons.thumb_up_alt_outlined, color: Colors.green),
                        tooltip: 'Helpful',
                      ),
                      IconButton(
                        onPressed: () => _submitFeedback(false),
                        icon: const Icon(Icons.thumb_down_alt_outlined, color: Colors.red),
                        tooltip: 'Not helpful',
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  String _formatModelName(String key) {
    switch (key) {
      case 'logistic_regression':
        return 'TF-IDF Logistic Regression';
      case 'linear_svm':
        return 'Calibrated Linear SVM';
      case 'gradient_boosting':
        return 'HistGradientBoosting';
      case 'transformer':
        return 'Sequence Contextual Classifier';
      default:
        return key.replaceAll('_', ' ').toUpperCase();
    }
  }
}
