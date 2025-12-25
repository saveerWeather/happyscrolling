"""Email sending utilities"""
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to import resend, fall back to SMTP if not available
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend not installed, email functionality will be limited")

class EmailService:
    def __init__(self):
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.from_email = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
        self.from_name = os.getenv('FROM_NAME', 'Busyplates')

        if self.resend_api_key and RESEND_AVAILABLE:
            resend.api_key = self.resend_api_key
            logger.info("Email service configured with Resend")
        else:
            logger.warning("Resend API key not configured")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email using Resend"""
        if not self.resend_api_key:
            logger.error("Resend API key not configured")
            return False

        if not RESEND_AVAILABLE:
            logger.error("Resend package not installed")
            return False

        try:
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": to_email,
                "subject": subject,
                "html": html_body
            }

            if text_body:
                params["text"] = text_body

            resend.Emails.send(params)
            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_verification_email(self, to_email: str, token: str, base_url: str) -> bool:
        """Send email verification link"""
        verify_url = f"{base_url}/verify-email/{token}"

        html = f"""
        <html>
        <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #d97556, #b55533); padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="color: #faf8f3; margin: 0;">Verify Your Email</h1>
            </div>
            <div style="background: #faf8f3; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="color: #3a3832; font-size: 16px;">Welcome to Busyplates!</p>
                <p style="color: #3a3832; font-size: 16px;">Click the button below to verify your email address:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" style="background: linear-gradient(135deg, #d97556, #b55533); color: #faf8f3; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p style="color: #6f6b62; font-size: 14px;">Or copy this link: <br><a href="{verify_url}" style="color: #c96543;">{verify_url}</a></p>
                <p style="color: #6f6b62; font-size: 12px; margin-top: 30px;">This link expires in 24 hours.</p>
            </div>
        </body>
        </html>
        """

        text = f"""
        Welcome to Busyplates!

        Verify your email by clicking this link:
        {verify_url}

        This link expires in 24 hours.
        """

        return self.send_email(to_email, "Verify your Busyplates email", html, text)

    def send_password_reset_email(self, to_email: str, token: str, base_url: str) -> bool:
        """Send password reset link"""
        reset_url = f"{base_url}/reset-password/{token}"

        html = f"""
        <html>
        <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #d97556, #b55533); padding: 30px; border-radius: 10px 10px 0 0;">
                <h1 style="color: #faf8f3; margin: 0;">Reset Your Password</h1>
            </div>
            <div style="background: #faf8f3; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="color: #3a3832; font-size: 16px;">You requested a password reset for your Busyplates account.</p>
                <p style="color: #3a3832; font-size: 16px;">Click the button below to reset your password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: linear-gradient(135deg, #d97556, #b55533); color: #faf8f3; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #6f6b62; font-size: 14px;">Or copy this link: <br><a href="{reset_url}" style="color: #c96543;">{reset_url}</a></p>
                <p style="color: #6f6b62; font-size: 12px; margin-top: 30px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
            </div>
        </body>
        </html>
        """

        text = f"""
        Reset your Busyplates password:
        {reset_url}

        This link expires in 1 hour.
        If you didn't request this, ignore this email.
        """

        return self.send_email(to_email, "Reset your Busyplates password", html, text)

email_service = EmailService()
