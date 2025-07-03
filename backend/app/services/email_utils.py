from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

async def send_verification_email(to_email: str, token: str):
    gmail_user = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    link = f"http://localhost:8000/api/auth/verify-email?token={token}"
    body = f"Click this link to verify your account:\n\n{link}"

    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = "Verify your ReadIQ Account"
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, app_password)
            server.send_message(msg)
        print(f"✅ Verification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email send failed: {e}")
