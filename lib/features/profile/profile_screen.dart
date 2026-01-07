import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../providers/theme_provider.dart';
import '../../core/app_strings.dart';
import '../../services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _profileData;
  bool _notificationsEnabled = true;

  void _toggleNotifications(bool value) {
    setState(() => _notificationsEnabled = value);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(value ? 'Notifications enabled' : 'Notifications disabled'),
        duration: const Duration(seconds: 1),
      ),
    );
  }

  void _showPlaceholderAction(String title) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: const Text('This feature is coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final data = await AuthService().fetchCurrentUserProfile();
    if (mounted) {
      setState(() {
        _profileData = data;
        _isLoading = false;
      });
    }
  }

  Future<void> _logout() async {
    await AuthService().signOut();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        body: Center(
          child: CircularProgressIndicator(color: Theme.of(context).colorScheme.primary),
        ),
      );
    }

    final user = _profileData?['user'];
    final medical = _profileData?['medical'];
    final name = user?['name'] ?? AppStrings.defaultUserName;
    final age = medical?['age_at_record']?.toString() ?? AppStrings.notAvailable;
    final gender = medical?['gender'] ?? AppStrings.notAvailable;
    final conditions = medical?['existing_conditions'] ?? AppStrings.none;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          AppStrings.profileTitle,
          style: GoogleFonts.inter(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).textTheme.titleLarge?.color,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: Theme.of(context).iconTheme.color),
            onPressed: () {
              setState(() => _isLoading = true);
              _fetchProfile();
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // User Header
            Center(
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: Text(
                      name.isNotEmpty ? name[0].toUpperCase() : AppStrings.defaultUserInitial,
                      style: GoogleFonts.inter(
                        color: Theme.of(context).colorScheme.onPrimary,
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    name,
                    style: GoogleFonts.inter(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    "$gender, $age yrs",
                    style: GoogleFonts.inter(color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Settings Sections
            _buildSectionHeader(AppStrings.medicalProfileHeader),
            // ... inside _buildSectionHeader ...
            _buildSettingItem(AppStrings.knownConditions, conditions),
            _buildSettingItem(AppStrings.medications, AppStrings.none), 
            _buildSettingItem(
              AppStrings.emergencyContact,
              "Not Set", // Removed hardcoded phone number
            ),


            const SizedBox(height: 24),
            _buildSectionHeader(AppStrings.appSettingsHeader),
            _buildSwitchItem(
              AppStrings.notifications,
              _notificationsEnabled,
              _toggleNotifications,
            ),
            _buildSwitchItem(
              AppStrings.darkMode,
              Provider.of<ThemeProvider>(context).isDarkMode,
              (val) => Provider.of<ThemeProvider>(context, listen: false).toggleTheme(val),
            ),
            _buildActionItem(
              AppStrings.privacySecurity,
              Icons.lock_outline,
              () => _showPlaceholderAction(AppStrings.privacySecurity),
            ),
            _buildActionItem(
              AppStrings.helpSupport,
              Icons.help_outline,
              () => _showPlaceholderAction(AppStrings.helpSupport),
            ),

            const SizedBox(height: 32),
            OutlinedButton(
              onPressed: _logout,
              style: OutlinedButton.styleFrom(
                foregroundColor: Theme.of(context).colorScheme.error,
                side: BorderSide(color: Theme.of(context).colorScheme.error),
                padding: const EdgeInsets.symmetric(
                  horizontal: 40,
                  vertical: 16,
                ),
              ),
              child: const Text(AppStrings.logOut),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 18,
            fontWeight: FontWeight.w700, // Bold
            color: Theme.of(
              context,
            ).textTheme.titleLarge?.color, // Black anchor
          ),
        ),
      ),
    );
  }

  Widget _buildSettingItem(String title, String value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        trailing: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 200),
          child: Text(
            value,
            style: GoogleFonts.inter(color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6)),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    );
  }

  Widget _buildSwitchItem(String title, bool value, ValueChanged<bool> onChanged) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: SwitchListTile(
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        value: value,
        onChanged: onChanged,
        activeThumbColor: Theme.of(context).colorScheme.primary,
      ),
    );
  }

  Widget _buildActionItem(String title, IconData icon, VoidCallback onTap) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: Theme.of(context).iconTheme.color),
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
