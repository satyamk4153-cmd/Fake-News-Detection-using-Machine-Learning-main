import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ModelsScreen extends StatefulWidget {
  const ModelsScreen({super.key});

  @override
  State<ModelsScreen> createState() => _ModelsScreenState();
}

class _ModelsScreenState extends State<ModelsScreen> {
  final ApiService _api = ApiService();
  List<Map<String, dynamic>> _models = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadModels();
  }

  Future<void> _loadModels() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final models = await _api.getModels();
      if (!mounted) return;
      setState(() {
        _models = models;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registered Models', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadModels,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, color: Colors.red, size: 40),
                        const SizedBox(height: 10),
                        Text(_error!, textAlign: TextAlign.center, style: const TextStyle(fontSize: 13)),
                        const SizedBox(height: 12),
                        ElevatedButton(onPressed: _loadModels, child: const Text('Retry')),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _models.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final m = _models[index];
                    final metrics = m['metrics'] as Map<String, dynamic>?;
                    final isProd = m['status'] == 'PRODUCTION';

                    return Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: isProd ? Colors.black87 : Colors.grey.shade300,
                          width: isProd ? 1.5 : 1.0,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                m['version_tag']?.toString() ?? '',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontFamily: 'monospace',
                                  color: Colors.grey.shade600,
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: isProd ? Colors.black87 : Colors.grey.shade200,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  m['status']?.toString() ?? 'EVALUATED',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: isProd ? Colors.white : Colors.grey.shade700,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            m['model_type']?.toString() ?? 'Model',
                            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                          if (metrics != null) ...[
                            const SizedBox(height: 12),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _metricBox(
                                  'Accuracy',
                                  '${((metrics['accuracy'] as num? ?? 0) * 100).toStringAsFixed(1)}%',
                                ),
                                _metricBox(
                                  'F1-Score',
                                  (metrics['f1'] as num? ?? 0).toStringAsFixed(3),
                                ),
                                _metricBox(
                                  'Brier Score',
                                  (metrics['brier_score'] as num? ?? 0).toStringAsFixed(4),
                                ),
                                if (metrics.containsKey('expected_calibration_error'))
                                  _metricBox(
                                    'ECE',
                                    (metrics['expected_calibration_error'] as num? ?? 0).toStringAsFixed(4),
                                  ),
                              ],
                            ),
                          ],
                        ],
                      ),
                    );
                  },
                ),
    );
  }

  Widget _metricBox(String title, String value) {
    return Column(
      children: [
        Text(title, style: TextStyle(fontSize: 10, color: Colors.grey.shade600)),
        const SizedBox(height: 2),
        Text(
          value,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }
}
