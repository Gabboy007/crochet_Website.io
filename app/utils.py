import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_folder):
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        return None

    original_name = secure_filename(file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)

    return f"uploads/{unique_name}"


def delete_uploaded_file(file_relative_path, static_folder):
    if not file_relative_path:
        return

    if file_relative_path.startswith("images/"):
        return

    absolute_path = os.path.join(static_folder, file_relative_path)
    if os.path.exists(absolute_path):
        os.remove(absolute_path)