import os
import json
import mimetypes
import smtplib
import uuid
from email.message import EmailMessage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
EMAIL_SETTING_KEYS = {
    "CONTACT_EMAIL",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_USE_TLS",
    "SMTP_SENDER",
}


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


def settings_file_path(instance_path):
    return os.path.join(instance_path, "site_settings.json")


def load_site_settings(instance_path):
    path = settings_file_path(instance_path)
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as settings_file:
        settings = json.load(settings_file)

    return {key: value for key, value in settings.items() if key in EMAIL_SETTING_KEYS}


def save_site_settings(instance_path, settings):
    path = settings_file_path(instance_path)
    os.makedirs(instance_path, exist_ok=True)

    cleaned_settings = {
        key: value
        for key, value in settings.items()
        if key in EMAIL_SETTING_KEYS and value not in (None, "")
    }

    with open(path, "w", encoding="utf-8") as settings_file:
        json.dump(cleaned_settings, settings_file, indent=2)


def email_settings_from_config(config, instance_path):
    settings = {key: config.get(key) for key in EMAIL_SETTING_KEYS}
    settings.update(load_site_settings(instance_path))

    if settings.get("SMTP_PORT"):
        settings["SMTP_PORT"] = int(settings["SMTP_PORT"])
    if isinstance(settings.get("SMTP_USE_TLS"), str):
        settings["SMTP_USE_TLS"] = settings["SMTP_USE_TLS"].strip().lower() in {"1", "true", "yes", "on"}
    if settings.get("SMTP_SENDER") in (None, ""):
        settings["SMTP_SENDER"] = settings.get("SMTP_USERNAME") or settings.get("CONTACT_EMAIL")

    return settings


def send_custom_order_email(config, order_data):
    required_settings = [
        config.get("SMTP_HOST"),
        config.get("SMTP_PORT"),
        config.get("SMTP_USERNAME"),
        config.get("SMTP_PASSWORD"),
        config.get("CONTACT_EMAIL"),
    ]
    if not all(required_settings):
        raise RuntimeError("Email settings are incomplete.")

    name = order_data["name"]
    customer_email = order_data["email"]
    product = order_data["product"]
    colors = order_data.get("colors") or "Not specified"
    message = order_data.get("message") or "No extra details provided."

    email = EmailMessage()
    email["Subject"] = f"New custom crochet order from {name}"
    email["From"] = config["SMTP_SENDER"]
    email["To"] = config["CONTACT_EMAIL"]
    email["Reply-To"] = customer_email
    email.set_content(
        "\n".join(
            [
                "New custom crochet order request",
                "",
                f"Name: {name}",
                f"Email: {customer_email}",
                f"Product type: {product}",
                f"Preferred colors: {colors}",
                "",
                "Custom details:",
                message,
            ]
        )
    )

    reference_image = order_data.get("reference_image")
    if reference_image and reference_image.filename:
        if not allowed_file(reference_image.filename):
            raise RuntimeError("Reference image must be PNG, JPG, JPEG, GIF, or WEBP.")

        original_name = secure_filename(reference_image.filename)
        image_data = reference_image.read()
        content_type = reference_image.mimetype or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
        maintype, subtype = content_type.split("/", 1)

        email.add_attachment(
            image_data,
            maintype=maintype,
            subtype=subtype,
            filename=original_name,
        )

    with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"], timeout=15) as server:
        if config.get("SMTP_USE_TLS"):
            server.starttls()
        server.login(config["SMTP_USERNAME"], config["SMTP_PASSWORD"])
        server.send_message(email)
