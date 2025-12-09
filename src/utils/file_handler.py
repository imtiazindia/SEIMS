"""
File upload and management utilities
"""

import os
import uuid
from typing import Optional
import streamlit as st

def save_uploaded_file(uploaded_file, upload_dir: str = "uploads") -> Optional[str]:
    """
    Save uploaded file and return file path
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        upload_dir: Directory to save files
        
    Returns:
        str: File path if successful, None otherwise
    """
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def validate_file_type(uploaded_file, allowed_types: list) -> bool:
    """
    Validate uploaded file type
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        allowed_types: List of allowed file extensions
        
    Returns:
        bool: True if file type is allowed
    """
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    return file_extension in [ext.lower() for ext in allowed_types]

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

