from langchain_core.tools import tool
from src.utils.cloudinary import upload_file_to_cloudinary


def _create_multimodal_content(file_path: str, content_type: str) -> dict:
    """
    Upload file to Cloudinary and create multimodal content structure.
    """
    result = upload_file_to_cloudinary(file_path)

    if "error" in result:
        return {"type": "error", "content": result["error"]}

    return {
        "type": "multimodal",
        "content": [
            {
                "type": "text",
                "text": f"{content_type.title()} uploaded successfully and ready for analysis.",
            },
            {"type": content_type, "source_type": "url", "url": result["url"]},
        ],
    }


@tool
def read_image(path: str) -> dict:
    """
    Upload an image to Cloudinary and return multimodal content for LLM processing.

    Args:
        path: The local path to the image file (e.g., 'images/photo.jpg').
    """
    return _create_multimodal_content(path, "image")


@tool
def read_audio(path: str) -> dict:
    """
    Upload an audio file to Cloudinary and return multimodal content for LLM processing.

    Args:
        path: The local path to the audio file (e.g., 'audio/recording.mp3').
    """
    return _create_multimodal_content(path, "audio")


@tool
def read_video(path: str) -> dict:
    """
    Upload a video file to Cloudinary and return multimodal content for LLM processing.

    Args:
        path: The local path to the video file (e.g., 'videos/clip.mp4').
    """
    return _create_multimodal_content(path, "video")
