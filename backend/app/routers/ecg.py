"""
ECG Session Router
Endpoints for ECG sessions, questionnaires, and snapshots
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from ..utils.auth import get_current_user, CurrentUser
from ..models.ecg import QuestionnaireCreate, QuestionnaireResponse, ECGSessionResponse
from ..services.supabase_service import SupabaseService
from ..services.storage_service import StorageService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/questionnaire", response_model=QuestionnaireResponse)
async def save_questionnaire(
    questionnaire: QuestionnaireCreate,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Save pre-monitoring questionnaire for an ECG session
    
    This captures the patient's context before the ECG recording:
    - Caffeine/nicotine consumption
    - Activity level
    - Stress score
    - Time of day
    """
    service = SupabaseService()
    result = await service.save_questionnaire(user.id, questionnaire)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to save questionnaire"
        )
    
    return result


@router.post("/snapshot/{reading_id}")
async def upload_snapshot(
    reading_id: int,
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user)
):
    """
    Upload ECG chart snapshot image
    
    Uploads the rendered ECG waveform image to Supabase Storage
    and updates the ecg_readings table with the image URL.
    """
    # Validate file type
    if file.content_type not in ["image/png", "image/jpeg", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PNG, JPEG, or WebP images are allowed"
        )
    
    # Limit file size (5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    storage = StorageService()
    url = await storage.upload_ecg_image(reading_id, contents, file.content_type)
    
    # Update ecg_readings with image URL
    service = SupabaseService()
    await service.update_ecg_image_url(reading_id, url)
    
    return {"image_url": url, "reading_id": reading_id}


@router.get("/session/{reading_id}", response_model=ECGSessionResponse)
async def get_session(
    reading_id: int,
    user: CurrentUser = Depends(get_current_user)
):
    """
    Get complete ECG session with questionnaire
    
    Returns the ECG reading data along with:
    - Heart rate statistics
    - Questionnaire responses
    - Snapshot URL (if available)
    """
    service = SupabaseService()
    session = await service.get_complete_session(reading_id, user.id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.get("/sessions", response_model=list[ECGSessionResponse])
async def list_sessions(
    limit: int = 10,
    offset: int = 0,
    user: CurrentUser = Depends(get_current_user)
):
    """
    List user's ECG sessions
    
    Returns paginated list of ECG sessions for the current user.
    """
    service = SupabaseService()
    sessions = await service.get_user_sessions(user.id, limit, offset)
    return sessions
