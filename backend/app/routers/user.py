"""
User Router
Endpoints for user profile and medications
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..utils.auth import get_current_user, CurrentUser
from ..models.user import UserProfile, Medication, MedicationCreate
from ..services.supabase_service import SupabaseService
from ..utils.sanitize import sanitize_notes

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get complete user profile with medical history
    
    Returns:
    - Basic user info (name, age)
    - Medical history (conditions, medications)
    - Active medications list
    """
    service = SupabaseService()
    profile = await service.get_user_profile(user.id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return profile


@router.get("/medications", response_model=List[Medication])
async def get_medications(
    active_only: bool = True,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get user's medications
    
    Args:
        active_only: If true, only return active medications
    """
    service = SupabaseService()
    medications = await service.get_medications(user.id, active_only)
    return medications


@router.post("/medications", response_model=Medication)
async def add_medication(
    medication: MedicationCreate,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Add a new medication to user's profile
    
    The medication will be marked as active by default.
    """
    # Sanitize notes field
    if medication.notes:
        medication.notes = sanitize_notes(medication.notes)
    
    service = SupabaseService()
    result = await service.add_medication(user.id, medication)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add medication"
        )
    
    return result


@router.delete("/medications/{medication_id}")
async def deactivate_medication(
    medication_id: str,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Deactivate a medication (soft delete)
    
    Marks the medication as inactive rather than deleting it.
    """
    service = SupabaseService()
    success = await service.deactivate_medication(medication_id, user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    return {"message": "Medication deactivated"}
