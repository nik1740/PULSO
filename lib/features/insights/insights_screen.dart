import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';
import '../../models/ecg_data.dart';

class InsightsScreen extends StatefulWidget {
  final String? readingId;
  const InsightsScreen({super.key, this.readingId});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  bool _isLoading = true;
  AnalysisResult? _analysis;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchAnalysis();
  }

  @override
  void didUpdateWidget(InsightsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.readingId != widget.readingId) {
      _fetchAnalysis();
    }
  }

  Future<void> _fetchAnalysis() async {
    if (widget.readingId == null) {
      setState(() {
        _isLoading = false;
        _error = "No session selected. Please select a session from History.";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final data = await ApiService().getAnalysis(widget.readingId!);
      final analysis = AnalysisResult.fromJson(data);
      if (mounted) {
        setState(() {
          _analysis = analysis;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = "Could not load analysis. It might not be ready yet.";
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.backgroundLight,
      appBar: AppBar(
        title: Text(
          "AI Insights",
          style: GoogleFonts.outfit(
            fontWeight: FontWeight.bold,
            color: AppColors.textLight,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: Theme.of(context).iconTheme.color),
            onPressed: _fetchAnalysis,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 48, color: Colors.grey),
              const SizedBox(height: 16),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: GoogleFonts.inter(color: Colors.grey),
              ),
              const SizedBox(height: 20),
              if (widget.readingId == null)
                OutlinedButton(
                  onPressed: () => context.go('/history'),
                  child: const Text("Go to History"),
                ),
            ],
          ),
        ),
      );
    }

    if (_analysis == null) {
      return const Center(child: Text("No data available"));
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Assessment Card
          _buildAssessmentCard(),
          const SizedBox(height: 24),

          // Recommendations
          if (_analysis!.recommendations != null &&
              _analysis!.recommendations!.isNotEmpty) ...[
            Text(
              "Recommendations",
              style: GoogleFonts.outfit(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textLight,
              ),
            ),
            const SizedBox(height: 12),
            ..._analysis!.recommendations!.map(
              (rec) => _buildRecommendationCard(rec),
            ),
          ],

          if (_analysis!.diagnosisSummary != null) ...[
            const SizedBox(height: 24),
            Text(
              "Summary",
              style: GoogleFonts.outfit(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppColors.textLight,
              ),
            ),
            const SizedBox(height: 8),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  _analysis!.diagnosisSummary!,
                  style: GoogleFonts.inter(height: 1.5),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAssessmentCard() {
    final isNormal = _analysis!.prediction.toLowerCase().contains("normal");
    final color = isNormal
        ? AppColors.success
        : AppColors.error; // Or use RiskLevel if available

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isNormal
              ? [Colors.green.shade400, Colors.green.shade700]
              : [Colors.orange.shade400, Colors.red.shade700],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _analysis!.riskLevel?.toUpperCase() ?? "ANALYSIS",
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _analysis!.prediction,
            style: GoogleFonts.outfit(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Confidence: ${(_analysis!.confidenceScore * 100).toStringAsFixed(0)}%",
            style: GoogleFonts.outfit(
              color: Colors.white.withOpacity(0.9),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(String text) {
    // Split title/desc if formatted like "Title: Desc"
    String title = "Advice";
    String desc = text;
    if (text.contains(":")) {
      final parts = text.split(":");
      title = parts[0].trim();
      desc = parts.sublist(1).join(":").trim();
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              backgroundColor: AppColors.surfaceLight,
              child: const Icon(
                Icons.lightbulb_outline,
                color: AppColors.primary,
                size: 20,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.outfit(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    desc,
                    style: GoogleFonts.outfit(color: Colors.grey, fontSize: 13),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
