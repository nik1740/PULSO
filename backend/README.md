# PULSO ECG Analysis Backend

FastAPI backend for the PULSO ECG Analysis application.

## Features

- 🔐 JWT authentication via Supabase
- 🚦 Rate limiting on analysis endpoints
- 🧹 Input sanitization
- 🤖 Gemini AI-powered ECG analysis
- 📊 ECG session management
- 💊 Medication tracking

## Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase and Gemini API keys

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### ECG
- `POST /api/v1/ecg/questionnaire` - Save session questionnaire
- `POST /api/v1/ecg/snapshot/{reading_id}` - Upload ECG image
- `GET /api/v1/ecg/session/{reading_id}` - Get session details
- `GET /api/v1/ecg/sessions` - List user sessions

### Analysis
- `POST /api/v1/analysis/request/{reading_id}` - Request AI analysis
- `GET /api/v1/analysis/{reading_id}` - Get analysis results
- `GET /api/v1/analysis/history/list` - Get analysis history

### User
- `GET /api/v1/user/profile` - Get user profile
- `GET /api/v1/user/medications` - List medications
- `POST /api/v1/user/medications` - Add medication

## Security

- All endpoints require JWT authentication (except health check)
- Analysis endpoint is rate-limited to 5 requests/hour
- Input sanitization prevents XSS attacks
