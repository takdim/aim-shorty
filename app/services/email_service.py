from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail


def send_verification_email(user, token: str) -> None:
    """Send email verification link."""
    from flask import url_for
    verify_url = url_for("auth.verify_email", token=token, _external=True)

    msg = Message(
        subject="Verifikasi Email Anda — LinkCraft",
        recipients=[user.email],
        html=render_template("emails/verify_email.html", user=user, verify_url=verify_url),
    )
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {e}")


def send_reset_email(user, token: str) -> None:
    """Send password reset link."""
    from flask import url_for
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    msg = Message(
        subject="Reset Password — LinkCraft",
        recipients=[user.email],
        html=render_template("emails/reset_password.html", user=user, reset_url=reset_url),
    )
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send reset email: {e}")
