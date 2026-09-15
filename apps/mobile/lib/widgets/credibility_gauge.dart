import 'package:flutter/material.dart';

class CredibilityGauge extends StatelessWidget {
  final double probability; // 0.0 to 1.0 (Credible)
  final String label;
  final int confidence;
  final String modelAgreement;

  const CredibilityGauge({
    super.key,
    required this.probability,
    required this.label,
    required this.confidence,
    required this.modelAgreement,
  });

  Color get statusColor {
    if (label.contains('CREDIBLE')) {
      return const Color(0xFF059669); // Emerald 600
    }
    if (label.contains('MISLEADING')) {
      return const Color(0xFFE11D48); // Rose 600
    }
    return const Color(0xFFD97706); // Amber 600
  }

  Color get backgroundColor {
    if (label.contains('CREDIBLE')) {
      return const Color(0xFFECFDF5); // Emerald 50
    }
    if (label.contains('MISLEADING')) {
      return const Color(0xFFFFF1F2); // Rose 50
    }
    return const Color(0xFFFFFBEB); // Amber 50
  }

  IconData get statusIcon {
    if (label.contains('CREDIBLE')) {
      return Icons.verified_user_rounded;
    }
    if (label.contains('MISLEADING')) {
      return Icons.warning_amber_rounded;
    }
    return Icons.help_outline_rounded;
  }

  @override
  Widget build(BuildContext context) {
    final clampedProb = probability.clamp(0.0, 1.0);
    final pct = (clampedProb * 100).toStringAsFixed(1);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor.withOpacity(0.3), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Icon(statusIcon, color: statusColor, size: 28),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'CALIBRATED ASSESSMENT',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.1,
                        color: Colors.grey.shade600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      label,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w900,
                        color: statusColor,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Calibrated probability progress bar
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Credibility Score',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey.shade700,
                ),
              ),
              Text(
                '$pct%',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w800,
                  fontFamily: 'monospace',
                  color: statusColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: clampedProb,
              minHeight: 10,
              backgroundColor: Colors.white,
              valueColor: AlwaysStoppedAnimation<Color>(statusColor),
            ),
          ),
          const SizedBox(height: 16),
          // Sub-metrics metadata row
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.8),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildSubMetric('Confidence', '$confidence%'),
                Container(width: 1, height: 20, color: Colors.grey.shade300),
                _buildSubMetric('Agreement', modelAgreement),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubMetric(String title, String value) {
    return Column(
      children: [
        Text(
          title,
          style: TextStyle(fontSize: 10, color: Colors.grey.shade600),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }
}
