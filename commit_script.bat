@echo off
cd /d c:\pulso\PULSO
git add pubspec.yaml pubspec.lock android/app/src/main/AndroidManifest.xml lib/features/ecg/device_pairing_screen.dart lib/features/ecg/ecg_screen.dart lib/screens/questionnaire_screen.dart
git commit -m "chore: Update dependencies and ECG screens"
git push origin main
echo Done > done.txt
