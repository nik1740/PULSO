"""
Gemini AI Service
Integration with Google Gemini for ECG analysis
Using direct REST API to avoid library compatibility issues
"""
import httpx
import json
import base64
import statistics
from typing import Dict, List, Optional

from ..config import get_settings


class GeminiService:
    """Service for Gemini AI ECG analysis"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.gemini_api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    async def analyze_ecg(
        self,
        session: Dict,
        user_profile: Dict,
        r_peaks: List[Dict]
    ) -> Dict:
        """
        Perform AI analysis on ECG session data
        
        Args:
            session: ECG session data with questionnaire
            user_profile: User profile with medical history
            r_peaks: R-peak detection data
            
        Returns:
            Analysis result dictionary
        """
        # Download image if available
        image_data = None
        if session.get("ecg_image_url"):
            image_data = await self._download_image(session["ecg_image_url"])
        
        # Build the analysis prompt
        prompt = self._build_prompt(session, user_profile, r_peaks)
        
        # Call Gemini API via REST
        try:
            result = await self._call_gemini_api(prompt, image_data)
            return self._parse_response(result)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                "prediction": f"Analysis unavailable: {str(e)}",
                "confidence_score": 0.0,
                "risk_level": "low",
                "recommendations": ["Please try again later or consult a healthcare professional"]
            }
    
    async def _call_gemini_api(self, prompt: str, image_data: Optional[bytes] = None) -> str:
        """Call Gemini API directly via REST"""
        url = f"{self.api_url}?key={self.api_key}"
        
        # Build request body
        parts = [{"text": prompt}]
        
        if image_data:
            parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": base64.b64encode(image_data).decode('utf-8')
                }
            })
        
        body = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract text from response
                candidates = data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return ""
            else:
                raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
    
    async def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            print(f"Error downloading image: {e}")
        return None
    
    def _build_prompt(
        self, 
        session: Dict, 
        profile: Dict, 
        r_peaks: List[Dict]
    ) -> str:
        """Build the analysis prompt for Gemini"""
        
        # Calculate HRV metrics
        hrv = self._calculate_hrv(r_peaks)
        
        # Extract data safely
        questionnaire = session.get("questionnaire", {})
        medical = profile.medical_history.__dict__ if profile and profile.medical_history else {}
        medications = profile.medications if profile else []
        med_names = ", ".join([m.medication_name for m in medications]) if medications else "None reported"
        
        prompt = f"""You are a medical AI assistant specialized in ECG analysis.
Analyze the following ECG data and provide insights.

## Patient Profile
- Age: {medical.get('age_at_record', 'Unknown')}
- Gender: {medical.get('gender', 'Unknown')}
- Existing Conditions: {medical.get('existing_conditions', 'None reported')}
- Current Medications: {med_names}

## Session Context
- Time of Day: {questionnaire.get('time_of_day', 'Unknown')}
- Caffeine Consumed (last 2 hrs): {questionnaire.get('caffeine_consumed', 'Unknown')}
- Nicotine Consumed: {questionnaire.get('nicotine_consumed', 'Unknown')}
- Activity Level: {questionnaire.get('activity_level', 'Unknown')}
- Stress Level: {questionnaire.get('stress_score', 'Unknown')}/5
- Additional Symptoms: {questionnaire.get('additional_symptoms', 'None')}

## ECG Session Metrics
- Duration: {session.get('duration_seconds', 0)} seconds
- Average Heart Rate: {session.get('average_heart_rate', 0):.1f} BPM
- Maximum Heart Rate: {session.get('max_heart_rate', 0):.1f} BPM
- Minimum Heart Rate: {session.get('min_heart_rate', 0):.1f} BPM
- R-Peak Count: {session.get('r_peak_count', 0)}
- HRV (SDNN): {hrv.get('sdnn', 0):.2f} ms
- HRV (RMSSD): {hrv.get('rmssd', 0):.2f} ms

Please provide your analysis in this exact JSON format:
{{
  "pattern_analysis": "Description of ECG patterns and any abnormalities observed",
  "heart_rate_assessment": "Assessment of heart rate, rhythm, and variability",
  "risk_level": "low|moderate|high|critical",
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "follow_up": "Guidance on when to seek medical attention",
  "confidence": 0.85
}}

IMPORTANT DISCLAIMER: This analysis is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional for medical concerns."""

        return prompt
    
    def _calculate_hrv(self, r_peaks: List[Dict]) -> Dict[str, float]:
        """Calculate Heart Rate Variability metrics from R-peaks"""
        if len(r_peaks) < 2:
            return {"sdnn": 0.0, "rmssd": 0.0}
        
        # Extract RR intervals
        rr_intervals = [
            p.get("rr_interval", 0) 
            for p in r_peaks 
            if p.get("rr_interval") and p.get("rr_interval") > 0
        ]
        
        if len(rr_intervals) < 2:
            return {"sdnn": 0.0, "rmssd": 0.0}
        
        try:
            # SDNN: Standard deviation of NN intervals
            sdnn = statistics.stdev(rr_intervals)
            
            # RMSSD: Root mean square of successive differences
            successive_diffs = [
                abs(rr_intervals[i+1] - rr_intervals[i]) 
                for i in range(len(rr_intervals) - 1)
            ]
            if successive_diffs:
                rmssd = (sum(d**2 for d in successive_diffs) / len(successive_diffs)) ** 0.5
            else:
                rmssd = 0.0
            
            return {"sdnn": sdnn, "rmssd": rmssd}
            
        except Exception:
            return {"sdnn": 0.0, "rmssd": 0.0}
    
    def _parse_response(self, text: str) -> Dict:
        """Parse Gemini response into structured data"""
        try:
            # Find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                data = json.loads(json_str)
                
                return {
                    "prediction": data.get("pattern_analysis", "") + "\n\n" + data.get("heart_rate_assessment", ""),
                    "confidence_score": float(data.get("confidence", 0.75)),
                    "risk_level": data.get("risk_level", "low"),
                    "recommendations": data.get("recommendations", []),
                    "diagnosis_summary": data.get("follow_up", "")
                }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing Gemini response: {e}")
        
        # Fallback: return raw text
        return {
            "prediction": text,
            "confidence_score": 0.5,
            "risk_level": "low",
            "recommendations": ["Please consult a healthcare professional for interpretation"]
        }
