import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/theme.dart';
import '../../services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  bool _isEditing = false;
  Map<String, dynamic>? _profileData;

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _ageController = TextEditingController();
  final TextEditingController _genderController = TextEditingController();
  final TextEditingController _conditionsController = TextEditingController();
  final TextEditingController _medicationsController =
      TextEditingController(); // Placeholder
  final TextEditingController _emergencyContactController =
      TextEditingController(); // Placeholder

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

        // Populate controllers
        final user = data?['user'];
        final medical = data?['medical'];

        _nameController.text = user?['name'] ?? '';
        _ageController.text = medical?['age_at_record']?.toString() ?? '';
        _genderController.text = medical?['gender'] ?? '';
        _conditionsController.text = medical?['existing_conditions'] ?? '';
        _medicationsController.text = medical?['current_medications'] ?? '';
      });
    }
  }

  Future<void> _saveProfile() async {
    setState(() => _isLoading = true);
    try {
      await AuthService().updateProfile(
        name: _nameController.text,
        age: int.tryParse(_ageController.text) ?? 0,
        gender: _genderController.text,
        conditions: _conditionsController.text,
        medications: _medicationsController.text,
        emergencyContact: _emergencyContactController.text,
      );
      setState(() {
        _isEditing = false;
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Profile Updated')));
      }
      _fetchProfile(); // Refresh
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  Future<void> _logout() async {
    await AuthService().signOut();
    if (mounted) context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: AppColors.backgroundLight,
        body: Center(
          child: CircularProgressIndicator(color: AppColors.primary),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Profile",
          style: GoogleFonts.inter(
            fontWeight: FontWeight.bold,
            color: Theme.of(context).textTheme.titleLarge?.color,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(
              _isEditing ? Icons.save : Icons.edit,
              color: Theme.of(context).iconTheme.color,
            ),
            onPressed: () {
              if (_isEditing) {
                _saveProfile();
              } else {
                setState(() => _isEditing = true);
              }
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
                    backgroundColor: AppColors.primary,
                    child: Text(
                      _nameController.text.isNotEmpty
                          ? _nameController.text[0].toUpperCase()
                          : 'U',
                      style: GoogleFonts.inter(
                        color: Colors.white,
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  _isEditing
                      ? TextField(
                          controller: _nameController,
                          textAlign: TextAlign.center,
                          style: GoogleFonts.inter(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                          decoration: const InputDecoration(
                            hintText: "Enter Name",
                            border: InputBorder.none,
                          ),
                        )
                      : Text(
                          _nameController.text.isNotEmpty
                              ? _nameController.text
                              : "User",
                          style: GoogleFonts.inter(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Settings Sections
            _buildSectionHeader("Medical Profile"),
            _buildEditableItem("Age", _ageController, numeric: true),
            _buildEditableItem("Gender", _genderController),
            _buildEditableItem("Known Conditions", _conditionsController),
            _buildEditableItem("Medications", _medicationsController),
            _buildEditableItem(
              "Emergency Contact",
              _emergencyContactController,
            ),

            const SizedBox(height: 24),
            _buildSectionHeader("App Settings"),
            _buildSwitchItem("Notifications", true),
            _buildSwitchItem("Dark Mode", false), // Logic to be implemented
            _buildActionItem("Privacy & Security", Icons.lock_outline),
            _buildActionItem("Help & Support", Icons.help_outline),

            const SizedBox(height: 32),
            if (_isEditing)
              OutlinedButton(
                onPressed: () {
                  setState(() {
                    _isEditing = false;
                    _fetchProfile(); // Revert
                  });
                },
                child: const Text("Cancel"),
              ),
            const SizedBox(height: 20),

            OutlinedButton(
              onPressed: _logout,
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.error,
                side: const BorderSide(color: AppColors.error),
                padding: const EdgeInsets.symmetric(
                  horizontal: 40,
                  vertical: 16,
                ),
              ),
              child: const Text("Log Out"),
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
            fontWeight: FontWeight.w700,
            color: Theme.of(context).textTheme.titleLarge?.color,
          ),
        ),
      ),
    );
  }

  Widget _buildEditableItem(
    String title,
    TextEditingController controller, {
    bool numeric = false,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        subtitle: _isEditing
            ? TextField(
                controller: controller,
                keyboardType: numeric
                    ? TextInputType.number
                    : TextInputType.text,
                decoration: const InputDecoration(isDense: true),
              )
            : Padding(
                padding: const EdgeInsets.only(top: 4.0),
                child: Text(
                  controller.text.isNotEmpty ? controller.text : 'Not set',
                  style: GoogleFonts.inter(color: Colors.grey),
                ),
              ),
      ),
    );
  }

  Widget _buildSwitchItem(String title, bool value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: SwitchListTile(
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        value: value,
        onChanged: (v) {},
        activeThumbColor: AppColors.primary,
      ),
    );
  }

  Widget _buildActionItem(String title, IconData icon) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: Theme.of(context).iconTheme.color),
        title: Text(
          title,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {},
      ),
    );
  }
}
