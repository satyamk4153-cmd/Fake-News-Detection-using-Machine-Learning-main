import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/analysis_model.dart';
import 'result_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _headlineController = TextEditingController();
  final TextEditingController _textController = TextEditingController();
  final TextEditingController _urlController = TextEditingController();

  bool _isLoading = false;
  String _loadingMessage = '';
  String? _errorMessage;
  UserModel? _currentUser;

  static const _credibleHeadline =
      'Federal Reserve Holds Benchmark Rates Steady Following Inflation Moderation';
  static const _credibleText =
      'The Federal Reserve concluded its policy meeting Wednesday by maintaining its benchmark interest rate in the target range of 5.25% to 5.50%. Federal Reserve officials stated that inflation has eased over the past year but remains slightly above the central bank objective.';

  static const _misleadingHeadline =
      'BOMBSHELL: Secret Globalist Cabal Caught Poisoning Municipal Water with Mind-Control Nanochips!';
  static const _misleadingText =
      'SHOCKING EXPOSED PROOF! Whistleblowers have finally leaked classified military documents proving that deep state elites and global billionaires are secretly installing 5G liquid nanotechnology into city water supplies across the nation! They want you sick and compliant!';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _checkCurrentUser();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _headlineController.dispose();
    _textController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _checkCurrentUser() async {
    try {
      final token = await ApiService().getToken();
      if (token != null && token.isNotEmpty) {
        final user = await ApiService().getMe();
        if (!mounted) return;
        setState(() {
          _currentUser = user;
        });
      }
    } catch (_) {}
  }

  void _loadSample(String headline, String text) {
    setState(() {
      _tabController.animateTo(0);
      _headlineController.text = headline;
      _textController.text = text;
      _errorMessage = null;
    });
  }

  Future<void> _showAuthDialog() async {
    final emailCtrl = TextEditingController();
    final passCtrl = TextEditingController();
    bool isRegister = false;
    String? dialogError;
    bool dialogLoading = false;

    await showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setDialogState) {
            return AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: Text(
                _currentUser != null
                    ? 'Account Profile'
                    : (isRegister ? 'Create Account' : 'Sign In'),
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
              ),
              content: _currentUser != null
                  ? Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Signed in as:', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                        const SizedBox(height: 4),
                        Text(_currentUser!.email, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade200,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            _currentUser!.role,
                            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ),
                      ],
                    )
                  : Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (dialogError != null) ...[
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.red.shade50,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.red.shade200),
                            ),
                            child: Text(dialogError!, style: TextStyle(color: Colors.red.shade900, fontSize: 12)),
                          ),
                          const SizedBox(height: 10),
                        ],
                        TextField(
                          controller: emailCtrl,
                          keyboardType: TextInputType.emailAddress,
                          decoration: const InputDecoration(
                            labelText: 'Email Address',
                            prefixIcon: Icon(Icons.email_outlined, size: 18),
                          ),
                        ),
                        const SizedBox(height: 8),
                        TextField(
                          controller: passCtrl,
                          obscureText: true,
                          decoration: const InputDecoration(
                            labelText: 'Password',
                            prefixIcon: Icon(Icons.lock_outline, size: 18),
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextButton(
                          onPressed: () {
                            setDialogState(() {
                              isRegister = !isRegister;
                              dialogError = null;
                            });
                          },
                          child: Text(
                            isRegister
                                ? 'Already have an account? Sign In'
                                : "Don't have an account? Register",
                            style: const TextStyle(fontSize: 12),
                          ),
                        ),
                      ],
                    ),
              actions: [
                if (_currentUser != null) ...[
                  TextButton(
                    onPressed: () async {
                      await ApiService().logout();
                      if (!mounted) return;
                      setState(() {
                        _currentUser = null;
                      });
                      Navigator.pop(ctx);
                    },
                    child: const Text('Sign Out', style: TextStyle(color: Colors.red)),
                  ),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Close'),
                  ),
                ] else ...[
                  TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Cancel'),
                  ),
                  ElevatedButton(
                    onPressed: dialogLoading
                        ? null
                        : () async {
                            final email = emailCtrl.text.trim();
                            final pass = passCtrl.text.trim();
                            if (email.isEmpty || pass.isEmpty) {
                              setDialogState(() => dialogError = 'Please enter both email and password.');
                              return;
                            }
                            setDialogState(() {
                              dialogLoading = true;
                              dialogError = null;
                            });
                            try {
                              AuthTokenResponse tokenResp;
                              if (isRegister) {
                                tokenResp = await ApiService().register(email, pass);
                              } else {
                                tokenResp = await ApiService().login(email, pass);
                              }
                              if (!mounted) return;
                              setState(() {
                                _currentUser = tokenResp.user;
                              });
                              Navigator.pop(ctx);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Welcome, ${tokenResp.user.email}!')),
                              );
                            } catch (e) {
                              setDialogState(() {
                                dialogLoading = false;
                                dialogError = e.toString();
                              });
                            }
                          },
                    child: dialogLoading
                        ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                        : Text(isRegister ? 'Register' : 'Sign In'),
                  ),
                ],
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _analyze() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _loadingMessage = 'Initiating credibility assessment...';
    });

    try {
      AnalysisResponse response;
      final api = ApiService();

      if (_tabController.index == 2) {
        // URL
        final url = _urlController.text.trim();
        if (url.isEmpty) {
          throw ApiException('Please enter a valid news URL.');
        }
        setState(() => _loadingMessage = 'Scraping article with SSRF validation...');
        response = await api.analyzeUrl(url);
      } else {
        // Article or Headline
        final text = _textController.text.trim();
        final headline = _headlineController.text.trim();
        if (text.isEmpty) {
          throw ApiException('Please enter article text or a headline to evaluate.');
        }

        setState(() => _loadingMessage = 'Extracting linguistic and contextual signals...');
        response = await api.analyzeText(
          text: text,
          headline: headline.isNotEmpty ? headline : null,
          inputType: _tabController.index == 0 ? 'article' : 'headline',
        );
      }

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(analysis: response),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
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
        title: const Row(
          children: [
            Icon(Icons.shield_outlined, size: 22),
            SizedBox(width: 8),
            Text(
              'TruthLens',
              style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: -0.5),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(
              _currentUser != null ? Icons.account_circle : Icons.account_circle_outlined,
              color: _currentUser != null ? Colors.green.shade800 : null,
            ),
            tooltip: _currentUser != null ? _currentUser!.email : 'Sign In',
            onPressed: _showAuthDialog,
          ),
        ],
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header Card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Probabilistic Credibility Intelligence',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Analyze News Credibility',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Calibrated multi-model consensus, linguistic feature deviations, and claim attribution. TruthLens does not claim absolute truth.',
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade700, height: 1.4),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Quick Benchmark Samples
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _loadSample(_credibleHeadline, _credibleText),
                      icon: const Icon(Icons.check_circle_outline, color: Colors.green, size: 16),
                      label: const Text('Credible Sample', style: TextStyle(fontSize: 11)),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _loadSample(_misleadingHeadline, _misleadingText),
                      icon: const Icon(Icons.warning_amber, color: Colors.red, size: 16),
                      label: const Text('Misleading Sample', style: TextStyle(fontSize: 11)),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Tab selector
              Container(
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: Colors.black87,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  labelColor: Colors.white,
                  unselectedLabelColor: Colors.grey.shade700,
                  labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  indicatorSize: TabBarIndicatorSize.tab,
                  tabs: const [
                    Tab(text: 'Full Article'),
                    Tab(text: 'Headline'),
                    Tab(text: 'URL'),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.shade200),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Colors.red, size: 20),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Colors.red.shade900, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
              ],

              // Form fields
              AnimatedBuilder(
                animation: _tabController,
                builder: (context, _) {
                  if (_tabController.index == 2) {
                    // URL Input
                    return TextField(
                      controller: _urlController,
                      keyboardType: TextInputType.url,
                      decoration: InputDecoration(
                        labelText: 'Article URL',
                        hintText: 'https://www.reuters.com/world/...',
                        prefixIcon: const Icon(Icons.link),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        helperText: 'SSRF protected • HTTP/HTTPS only',
                      ),
                    );
                  }

                  return Column(
                    children: [
                      if (_tabController.index == 0) ...[
                        TextField(
                          controller: _headlineController,
                          decoration: InputDecoration(
                            labelText: 'Headline (Optional)',
                            hintText: 'Enter news headline...',
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],
                      TextField(
                        controller: _textController,
                        maxLines: _tabController.index == 0 ? 8 : 4,
                        decoration: InputDecoration(
                          labelText: _tabController.index == 0 ? 'Article Body Text' : 'Headline Text',
                          hintText: 'Paste news text to analyze credibility...',
                          alignLabelWithHint: true,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      ),
                    ],
                  );
                },
              ),

              const SizedBox(height: 20),

              // Submit Button
              ElevatedButton(
                onPressed: _isLoading ? null : _analyze,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black87,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isLoading
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          ),
                          const SizedBox(width: 12),
                          Text(_loadingMessage, style: const TextStyle(fontSize: 13)),
                        ],
                      )
                    : const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Analyze Credibility',
                            style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(width: 8),
                          Icon(Icons.arrow_forward, size: 18),
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
}
