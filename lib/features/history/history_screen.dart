import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../core/theme.dart';
import '../../models/ecg_data.dart';
import '../../services/ecg_storage_service.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  late Future<List<ECGSession>> _historyFuture;

  @override
  void initState() {
    super.initState();
    _historyFuture = _fetchHistory();
  }

  Future<List<ECGSession>> _fetchHistory() async {
    final user = Supabase.instance.client.auth.currentUser;
    if (user != null) {
      return await ECGStorageService().getRecentSessions(user.id, limit: 20);
    }
    return [];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "History",
          style: GoogleFonts.inter(
            fontWeight: FontWeight.bold,
            color: AppColors.textLight,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list, color: AppColors.textLight),
            onPressed: () {},
          ),
        ],
      ),
      body: FutureBuilder<List<ECGSession>>(
        future: _historyFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
             return Center(child: Text("Error loading history"));
          }

          final sessions = snapshot.data ?? [];

          if (sessions.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.grey[300]),
                  const SizedBox(height: 16),
                  Text(
                    "No history found",
                    style: GoogleFonts.inter(color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(16.0),
            itemCount: sessions.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              return _buildHistoryItem(context, sessions[index]);
            },
          );
        },
      ),
    );
  }

  Widget _buildHistoryItem(BuildContext context, ECGSession session) {
    // For now, we assume Normal unless flagged. 
    // You can add logic here to check abnormalitiesCount if added to schema later.
    bool isAbnormal = false; 

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: isAbnormal
                ? AppColors.error.withOpacity(0.1)
                : AppColors.surfaceHighlight.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.monitor_heart,
            color: isAbnormal ? AppColors.error : AppColors.primary,
          ),
        ),
        title: Text(
          isAbnormal ? "Irregular Rhythm" : "ECG Recording",
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
            Text(
               "Avg HR: ${session.averageHeartRate?.toStringAsFixed(0) ?? '--'} BPM",
               style: GoogleFonts.inter(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right, color: AppColors.textLight),
        onTap: () {
          // Pass the specific session data or ID to the report screen
          // context.go('/insights/report', extra: session);
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return "${date.day}/${date.month}/${date.year}";
  }
}