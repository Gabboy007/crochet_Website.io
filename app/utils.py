import os
import html
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


def build_custom_order_email_html(order_data):
    name = html.escape(order_data["name"])
    customer_email = html.escape(order_data["email"])
    product = html.escape(order_data["product"])
    colors = html.escape(order_data.get("colors") or "Not specified")
    message = html.escape(order_data.get("message") or "No extra details provided.").replace("\n", "<br>")

    return f"""\
<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#fff8fb;font-family:'Segoe UI',Arial,sans-serif;color:#433a57;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#fff8fb 0%,#f8f1ff 48%,#f4fff9 100%);padding:28px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:640px;background:#ffffff;border:1px solid #f0deef;border-radius:18px;overflow:hidden;box-shadow:0 18px 44px rgba(165,134,190,0.18);">
            <tr>
              <td style="padding:28px 30px;background:linear-gradient(135deg,#eadcff 0%,#ffddea 58%,#ddf6ea 100%);">
                <div style="display:inline-block;padding:7px 12px;border-radius:999px;background:rgba(255,255,255,0.72);border:1px solid rgba(255,255,255,0.85);color:#6b5a86;font-size:13px;font-weight:700;">
                  New custom order
                </div>
                <h1 style="margin:14px 0 6px;font-size:34px;line-height:1.08;color:#fff4d6;font-weight:900;-webkit-text-stroke:2px #6b4d45;text-shadow:1px 0 #6b4d45,-1px 0 #6b4d45,0 1px #6b4d45,0 -1px #6b4d45,2px 3px 0 #6b4d45,4px 6px 10px rgba(82,60,56,0.32);">
                  Minn Miru Handcrafted
                </h1>
                <p style="margin:0;color:#6b5a86;font-size:15px;line-height:1.6;">
                  A customer sent a crochet request from your website.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:26px 30px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="padding:0 0 14px;">
                      <h2 style="margin:0;color:#433a57;font-size:20px;line-height:1.3;">Customer Details</h2>
                    </td>
                  </tr>
                </table>

                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border-spacing:0 10px;">
                  <tr>
                    <td style="width:150px;padding:12px 14px;background:#fff8fb;border-radius:12px 0 0 12px;color:#7d7391;font-size:13px;font-weight:700;">Name</td>
                    <td style="padding:12px 14px;background:#fff8fb;border-radius:0 12px 12px 0;color:#433a57;font-size:15px;font-weight:700;">{name}</td>
                  </tr>
                  <tr>
                    <td style="width:150px;padding:12px 14px;background:#f8f1ff;border-radius:12px 0 0 12px;color:#7d7391;font-size:13px;font-weight:700;">Email</td>
                    <td style="padding:12px 14px;background:#f8f1ff;border-radius:0 12px 12px 0;color:#433a57;font-size:15px;">
                      <a href="mailto:{customer_email}" style="color:#6b5a86;text-decoration:none;font-weight:700;">{customer_email}</a>
                    </td>
                  </tr>
                  <tr>
                    <td style="width:150px;padding:12px 14px;background:#f4fff9;border-radius:12px 0 0 12px;color:#7d7391;font-size:13px;font-weight:700;">Product Type</td>
                    <td style="padding:12px 14px;background:#f4fff9;border-radius:0 12px 12px 0;color:#433a57;font-size:15px;font-weight:700;">{product}</td>
                  </tr>
                  <tr>
                    <td style="width:150px;padding:12px 14px;background:#fffaf0;border-radius:12px 0 0 12px;color:#7d7391;font-size:13px;font-weight:700;">Colors</td>
                    <td style="padding:12px 14px;background:#fffaf0;border-radius:0 12px 12px 0;color:#433a57;font-size:15px;">{colors}</td>
                  </tr>
                </table>

                <div style="margin-top:18px;padding:18px;border-radius:16px;background:#ffffff;border:1px solid #f0deef;">
                  <div style="color:#7d7391;font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:0.04em;">Custom details</div>
                  <p style="margin:10px 0 0;color:#433a57;font-size:15px;line-height:1.75;">{message}</p>
                </div>

                <div style="margin-top:20px;padding:14px 16px;border-radius:14px;background:#fff8fb;color:#7d7391;font-size:13px;line-height:1.6;">
                  Reply directly to this email to answer the customer. If they uploaded a reference image, it is attached to this message.
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:18px 30px;background:#fbfffd;border-top:1px solid #f0deef;color:#7d7391;font-size:12px;line-height:1.6;text-align:center;">
                Minn Miru Handcrafted custom order form
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


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
    email.add_alternative(build_custom_order_email_html(order_data), subtype="html")

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
