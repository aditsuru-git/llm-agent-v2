import os
from pathlib import Path
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_file_to_cloudinary(file_path: str) -> dict:
    """
    Upload a file to Cloudinary and return the public URL.

    Args:
        file_path: Local path to the file

    Returns:
        dict: Either {"url": "..."} or {"error": "..."}
    """
    p = Path(file_path)
    if not p.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="auto",  # Auto-detect file type
        )
        return {"url": result["secure_url"]}

    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}
