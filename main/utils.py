import os
import time
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_uploaded_file(upload: UploadedFile, subfolder: str) -> str:
    """Сохраняет загруженный файл в MEDIA_ROOT и возвращает относительный путь для БД."""
    if not upload or not upload.name:
        return ''
    if not allowed_file(upload.name):
        return ''
    name_base, ext = os.path.splitext(os.path.basename(upload.name))
    safe_name = f"{name_base}_{int(time.time())}{ext}"
    rel_path = os.path.join('uploads', subfolder, safe_name)
    full_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'wb') as f:
        for chunk in upload.chunks():
            f.write(chunk)
    return rel_path
