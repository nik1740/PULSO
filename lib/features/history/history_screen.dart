import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../core/theme.dart';
import '../../services/ecg_storage_service.dart';
import '../../models/ecg_data.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final ECGStorageService _storageService = ECGStorageService();
  List<ECGSession> _sessions = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchHistory();
  }

  Future<void> _fetchHistory() async {
    final user = Supabase.instance.client.auth.currentUser;
    if (user != null) {
      try {
        final sessions = await _storageService.getRecentSessions(
          user.id,
          limit: 10,
        );
        if (mounted) {
          setState(() {
            _sessions = sessions;
            _isLoading = false;
          });
        }
      } catch (e) {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      }
    } else {
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
        title: Text(
          "History",
          style: GoogleFonts.inter(
            fontWeight: FontWeight.bold,
            color: Theme.of(
              context,
            ).textTheme.titleLarge?.color, // Consistent theme
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: Theme.of(context).iconTheme.color),
            onPressed: () {
              setState(() => _isLoading = true);
              _fetchHistory();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _sessions.isEmpty
          ? Center(
              child: Text(
                "No recordings found",
                style: GoogleFonts.inter(color: Colors.grey),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16.0),
              itemCount: _sessions.length,
              separatorBuilder: (context, index) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                return _buildHistoryItem(context, _sessions[index]);
              },
            ),
    );
  }

  Widget _buildHistoryItem(BuildContext context, ECGSession session) {
    // Determine status (Mock logic until Analysis Result is linked)
    bool isAbnormal = false;
    final hr = session.averageHeartRate ?? 0;
    if (hr < 60 || hr > 100) isAbnormal = true;

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: isAbnormal
                ? AppColors.error.withOpacity(0.1)
                : AppColors.success.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.monitor_heart,
            color: isAbnormal ? AppColors.error : AppColors.success,
          ),
        ),
        title: Text(
          isAbnormal ? "Irregular Rhythm" : "Normal Sinus Rhythm",
          style: GoogleFonts.inter(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              "${_formatDate(session.startTime)} • ${session.durationSeconds}s",
              style: GoogleFonts.inter(fontSize: 12),
            ),
            if (isAbnormal)
              Padding(
                padding: const EdgeInsets.only(top: 4.0),
                child: Text(
                  "Action Required",
                  style: GoogleFonts.inter(
                    color: AppColors.error,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          // Pass the session ID to insights screen
          // Use extra or query params
          context.push('/insights', extra: session.id);
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return "${date.day}/${date.month} ${date.hour}:${date.minute.toString().padLeft(2, '0')}";
  }
}
