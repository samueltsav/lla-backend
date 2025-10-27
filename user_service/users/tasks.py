import redis
from celery.utils.log import get_task_logger
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, Any
from celery import Celery, shared_task
from user_service_config.django import base



logger = get_task_logger(__name__)

app = Celery("user_service_config")


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def send_login_notification_email(
    self, user_data: Dict[str, Any], login_info: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        logger.info(
            f"Starting email notification task for user: {user_data.get('email')}"
        )

        # Validate required data
        if not user_data.get("email"):
            raise ValueError("User email is required")

        # Prepare email content
        email_content = prepare_login_email_content(user_data, login_info)

        # Send email
        send_email(
            to_email=user_data["email"],
            subject=email_content["subject"],
            html_body=email_content["html_body"],
            text_body=email_content["text_body"],
        )

        logger.info(
            f"Login notification email sent successfully to {user_data['email']}"
        )

        return {
            "status": "success",
            "message": "Login notification email sent successfully",
            "recipient": user_data["email"],
            "timestamp": datetime.now,
            "task_id": self.request.id,
        }

    except Exception as exc:
        logger.error(f"Failed to send login notification email: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
)
def send_suspicious_login_alert(
    self, user_data: Dict[str, Any], login_info: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        logger.warning(
            f"Sending suspicious login alert for user: {user_data.get('email')}"
        )

        # Prepare alert email content
        email_content = prepare_suspicious_login_email_content(user_data, login_info)

        # Send high priority email
        send_email(
            to_email=user_data["email"],
            subject=email_content["subject"],
            html_body=email_content["html_body"],
            text_body=email_content["text_body"],
            priority="high",
        )

        logger.info(f"Suspicious login alert sent successfully to {user_data['email']}")

        return {
            "status": "success",
            "message": "Suspicious login alert sent successfully",
            "recipient": user_data["email"],
            "timestamp": datetime.now,
            "task_id": self.request.id,
            "alert_type": "suspicious_login",
        }

    except Exception as exc:
        logger.error(f"Failed to send suspicious login alert: {str(exc)}")
        raise self.retry(exc=exc, countdown=30, max_retries=2)


def prepare_login_email_content(
    user_data: Dict[str, Any], login_info: Dict[str, Any]
) -> Dict[str, str]:
    user_name = user_data.get("name", user_data.get("email", "User"))
    login_time = login_info.get(
        "timestamp", datetime.now.strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    ip_address = login_info.get("ip_address", "Unknown")
    location = login_info.get("location", "Unknown")
    device_info = login_info.get("device_info", "Unknown")
    browser = login_info.get("browser", "Unknown")

    f"Login Notification - {user_name}"

    f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #f9f9f9; padding: 20px; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .info-table th, .info-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            .info-table th {{ background-color: #f2f2f2; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Login Notification</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>We detected a successful login to your account. Here are the details:</p>
                
                <table class="info-table">
                    <tr><th>Time</th><td>{login_time}</td></tr>
                    <tr><th>IP Address</th><td>{ip_address}</td></tr>
                    <tr><th>Location</th><td>{location}</td></tr>
                    <tr><th>Device</th><td>{device_info}</td></tr>
                    <tr><th>Browser</th><td>{browser}</td></tr>
                </table>
                
                <p>If this was you, you can safely ignore this email.</p>
                <p><strong>If this wasn"t you:</strong></p>
                <ul>
                    <li>Change your password immediately</li>
                    <li>Review your account activity</li>
                    <li>Contact our support team</li>
                </ul>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>© 2024 Your Company Name. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def prepare_suspicious_login_email_content(
    user_data: Dict[str, Any], login_info: Dict[str, Any]
) -> Dict[str, str]:
    user_name = user_data.get("name", user_data.get("email", "User"))
    login_time = login_info.get(
        "timestamp", datetime.now.strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    ip_address = login_info.get("ip_address", "Unknown")
    location = login_info.get("location", "Unknown")
    suspicious_reasons = login_info.get("suspicious_reasons", [])

    f"🚨 SECURITY ALERT: Suspicious Login Detected - {user_name}"

    reasons_html = (
        "<ul>"
        + "".join([f"<li>{reason}</li>" for reason in suspicious_reasons])
        + "</ul>"
    )

    f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
            .content {{ background-color: #fff3cd; padding: 20px; border: 2px solid #f44336; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .info-table th, .info-table td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            .info-table th {{ background-color: #f2f2f2; }}
            .alert {{ background-color: #f8d7da; padding: 15px; margin: 20px 0; border-left: 4px solid #f44336; }}
            .action-buttons {{ text-align: center; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #f44336; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 SECURITY ALERT</h1>
                <h2>Suspicious Login Detected</h2>
            </div>
            <div class="content">
                <div class="alert">
                    <strong>IMMEDIATE ACTION REQUIRED!</strong><br>
                    We detected a suspicious login attempt on your account.
                </div>
                
                <h3>Hello {user_name},</h3>
                <p>Our security systems flagged a login attempt that appears suspicious:</p>
                
                <table class="info-table">
                    <tr><th>Time</th><td>{login_time}</td></tr>
                    <tr><th>IP Address</th><td>{ip_address}</td></tr>
                    <tr><th>Location</th><td>{location}</td></tr>
                </table>
                
                <h3>Why this login is suspicious:</h3>
                {reasons_html}
                
                <div class="action-buttons">
                    <a href="#" class="button">Change Password Now</a>
                    <a href="#" class="button">Review Account Activity</a>
                </div>
                
                <p><strong>If this was NOT you:</strong></p>
                <ol>
                    <li>Change your password immediately</li>
                    <li>Enable two-factor authentication</li>
                    <li>Review recent account activity</li>
                    <li>Contact our security team immediately</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str,
    priority: str = "normal",
) -> bool:
    try:
        # Validate email configuration
        if not base.DEFAULT_FROM_EMAIL:
            raise ValueError("Email credentials not configured")

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = base.DEFAULT_FROM_EMAIL
        message["To"] = to_email

        # Set priority
        if priority == "high":
            message["X-Priority"] = "1"
            message["X-MSMail-Priority"] = "High"

        # Create text and HTML parts
    
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Create secure connection and send email
        context = ssl.create_default_context()

        with smtplib.SMTP(
            base.AZURE_EMAIL_CONNECTION_STRING, base.EMAIL_PORT
        ) as server:
            if base.use_tls:
                server.starttls(context=context)

            server.login(base.DEFAULT_FROM_EMAIL)
            server.sendmail(base.DEFAULT_FROM_EMAIL, to_email, message.as_string())

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise


# Cleanup task
r = redis.Redis(host="redis", port=6379, db=0)


@shared_task
def cleanup_old_results(days: int = 7):
    try:
        (timezone.now() - timedelta(days=days)).timestamp()
        deleted = 0

        for key in r.scan_iter("celery-task-meta-*"):
            r.get(key)
            # Optionally parse timestamp if you stored one
            r.delete(key)
            deleted += 1

        return {"status": "success", "message": f"{deleted} old results cleaned up"}
    except Exception as e:
        raise RuntimeError(f"Failed cleanup: {str(e)}")
