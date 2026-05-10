import os
from io import BytesIO
from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def allowed_filename(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_image_file(file_stream, filename: str) -> bool:
    """Validate image by extension and attempting to open with Pillow.

    `file_stream` should be a file-like object (BytesIO or werkzeug FileStorage.stream).
    Returns True if valid and size <= MAX_IMAGE_BYTES.
    """
    if not allowed_filename(filename):
        return False

    # read into memory-safe buffer up to limit
    data = file_stream.read()
    if not data:
        return False
    if len(data) > MAX_IMAGE_BYTES:
        return False

    try:
        img = Image.open(BytesIO(data))
        img.verify()
    except UnidentifiedImageError:
        return False
    except Exception:
        return False

    return True


def save_image_file(file_storage, dest_folder: str, filename: str) -> str:
    """Save uploaded file to dest_folder with secure filename. Returns relative path."""
    os.makedirs(dest_folder, exist_ok=True)
    path = os.path.join(dest_folder, filename)
    # file_storage may be werkzeug FileStorage
    file_storage.save(path)
    return path
