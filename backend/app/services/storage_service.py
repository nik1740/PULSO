"""
Storage Service
Supabase Storage operations for ECG snapshot images
"""
from typing import Optional
import uuid

from ..database import get_storage_client


class StorageService:
    """Service for Supabase Storage operations"""
    
    BUCKET_NAME = "ecg-snapshots"
    
    def __init__(self):
        self.storage = get_storage_client()
    
    async def upload_ecg_image(
        self, 
        reading_id: int, 
        image_data: bytes,
        content_type: str = "image/png"
    ) -> str:
        """
        Upload ECG chart snapshot to Supabase Storage
        
        Returns the public URL of the uploaded image
        """
        # Generate unique filename
        file_ext = self._get_extension(content_type)
        filename = f"{reading_id}/{uuid.uuid4().hex}.{file_ext}"
        
        try:
            # Upload to storage
            result = self.storage.from_(self.BUCKET_NAME).upload(
                path=filename,
                file=image_data,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            url = self.storage.from_(self.BUCKET_NAME).get_public_url(filename)
            return url
            
        except Exception as e:
            print(f"Error uploading image: {e}")
            raise
    
    def _get_extension(self, content_type: str) -> str:
        """Get file extension from content type"""
        mapping = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/webp": "webp",
        }
        return mapping.get(content_type, "png")
    
    async def delete_image(self, path: str) -> bool:
        """Delete an image from storage"""
        try:
            self.storage.from_(self.BUCKET_NAME).remove([path])
            return True
        except:
            return False
