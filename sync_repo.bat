@echo off
echo Starting Sync... > sync_log.txt
echo Staging files... >> sync_log.txt
git add lib/features/ecg/ecg_screen.dart android/app/src/main/AndroidManifest.xml packages/flutter_bluetooth_serial/pubspec.yaml >> sync_log.txt 2>&1
echo Committing... >> sync_log.txt
git commit -m "feat(ecg): implement live view, premium UI and permissions" >> sync_log.txt 2>&1
echo Pulling... >> sync_log.txt
git pull --rebase origin main >> sync_log.txt 2>&1
echo Pushing... >> sync_log.txt
git push origin main >> sync_log.txt 2>&1
echo Done. >> sync_log.txt
