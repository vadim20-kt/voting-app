import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import secrets
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def generate_verification_token(length=32):
    """Generate a secure random token for email verification."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_verification_email(email, token, user_id, base_url):
    """Send a verification email with the verification link."""
    try:
        # Create the email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Verifică adresa ta de email - Aplicația de Vot"
        msg['From'] = f"{os.getenv('EMAIL_FROM_NAME', 'Aplicația de Vot')} <{os.getenv('EMAIL_FROM')}>"
        msg['To'] = email

        # Create the verification link
        verification_url = f"{base_url}/verify-email?token={token}&user_id={user_id}"

        # Create the HTML version of the message
        html = f"""
        <html>
          <body>
            <h2>Bine ai venit la Aplicația de Vot!</h2>
            <p>Vă mulțumim pentru înregistrare. Vă rugăm să vă verificați adresa de email făcând clic pe butonul de mai jos:</p>
            <p>
              <a href="{verification_url}" 
                 style="background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px;">
                Verifică email
              </a>
            </p>
            <p>Sau copiază și lipește acest link în browser:</p>
            <p>{verification_url}</p>
            <p>Acest link va expira în 24 de ore.</p>
          </body>
        </html>
        """

        # Attach the HTML content
        msg.attach(MIMEText(html, 'html'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
        
        logger.info(f"Email de verificare trimis către {email}")
        return True

    except Exception as e:
        logger.error(f"Eroare la trimiterea email-ului de verificare: {str(e)}")
        return False
