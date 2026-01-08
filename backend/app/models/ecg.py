"""
ECG Pydantic Models
Models for ECG sessions, questionnaires, and related data
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ActivityLevel(str, Enum):
    """Activity level before ECG recording"""
    AT_REST = "at_rest"
    POST_ACTIVITY = "post_activity"


class TimeOfDay(str, Enum):
    """Time of day for the recording session"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"


class QuestionnaireCreate(BaseModel):
    """Request model for creating a questionnaire"""
    reading_id: int = Field(..., description="ECG reading ID to associate with")
    caffeine_consumed: bool = Field(..., description="Caffeine in last 2 hours")
    nicotine_consumed: bool = Field(..., description="Nicotine since last recording")
    activity_level: ActivityLevel = Field(..., description="Current activity state")
    stress_score: int = Field(..., ge=1, le=5, description="Stress level 1-5")
    time_of_day: TimeOfDay = Field(..., description="Session time of day")
    additional_symptoms: Optional[str] = Field(None, max_length=500)


class QuestionnaireResponse(BaseModel):
    """Response model for questionnaire data"""
    id: str
    reading_id: int
    user_id: str
    caffeine_consumed: bool
    nicotine_consumed: bool
    activity_level: str
    stress_score: int
    time_of_day: str
    additional_symptoms: Optional[str] = None
    created_at: datetime


class ECGSessionResponse(BaseModel):
    """Complete ECG session with questionnaire"""
    reading_id: int
    user_id: str
    timestamp: datetime
    duration_seconds: Optional[int] = None
    average_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    min_heart_rate: Optional[float] = None
    r_peak_count: Optional[int] = None
    ecg_image_url: Optional[str] = None
    questionnaire: Optional[QuestionnaireResponse] = None


class RPeakData(BaseModel):
    """R-peak detection data"""
    sample_index: int
    timestamp: datetime
    rr_interval: float
    instantaneous_bpm: float
    amplitude: float
