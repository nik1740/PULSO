"""
User Pydantic Models
Models for user profiles and medications
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class MedicalHistory(BaseModel):
    """User's medical history"""
    age_at_record: Optional[int] = None
    gender: Optional[str] = None
    existing_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    last_checkup_date: Optional[date] = None


class Medication(BaseModel):
    """Medication record"""
    medication_id: str
    medication_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class MedicationCreate(BaseModel):
    """Request model for adding a medication"""
    medication_name: str = Field(..., min_length=1, max_length=200)
    dosage: Optional[str] = Field(None, max_length=100)
    frequency: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class UserProfile(BaseModel):
    """Complete user profile"""
    user_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[MedicalHistory] = None
    medications: List[Medication] = []
