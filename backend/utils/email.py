"""Email sending utilities"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'Busyplates')

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email

            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

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
