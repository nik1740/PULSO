# PULSO App - Environment Setup

## Setting Up Your Development Environment

### 1. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
- **Gemini API Key**: Get from https://aistudio.google.com/app/apikey

### 2. Running the App

**Option A: Using environment file (Recommended)**
```bash
flutter run -d <device_id> --dart-define-from-file=.env
```

**Option B: Direct command line**
```bash
flutter run -d <device_id> --dart-define=GEMINI_API_KEY=your_key_here
```

### 3. For Team Members

- Never commit `.env` file to git (it's in `.gitignore`)
- Each developer should create their own `.env` file from `.env.example`
- Get your own Gemini API key from Google AI Studio

## Notes

- The `.env` file is ignored by git for security
- `.env.example` is committed as a template for team members
- Each developer uses their own API keys
