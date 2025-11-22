"""
Serviciu pentru trimiterea email-urilor cu coduri de verificare
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Încearcă să încarce dotenv dacă este disponibil
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv nu este instalat, folosește variabilele de mediu sistem

# Configurare SMTP (din variabile de mediu sau valori default)
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'from_email': os.getenv('SMTP_FROM_EMAIL', 'noreply@vote.md'),
    'from_name': os.getenv('SMTP_FROM_NAME', 'Sistem Vot Electronic')
}

def send_verification_email(email, code, user_name=None):
    """
    Trimite codul de verificare prin email
    
    Args:
        email: Adresa de email destinatar
        code: Codul de verificare (6 cifre)
        user_name: Numele utilizatorului (opțional)
    
    Returns:
        bool: True dacă email-ul a fost trimis cu succes, False altfel
    """
    try:
        # Verifică dacă SMTP este configurat
        if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
            print(f"⚠️ SMTP nu este configurat. Cod pentru {email}: {code}")
            return False
        
        # Creează mesajul
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Cod de verificare - Sistem Vot Electronic'
        msg['From'] = f"{SMTP_CONFIG['from_name']} <{SMTP_CONFIG['from_email']}>"
        msg['To'] = email
        
        # Conținut HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: white; border: 2px dashed #667eea; 
                           padding: 20px; text-align: center; margin: 20px 0; 
                           border-radius: 10px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                        letter-spacing: 5px; font-family: monospace; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                          padding: 10px; margin: 15px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Cod de Verificare</h1>
                </div>
                <div class="content">
                    <p>Salut{f' {user_name}' if user_name else ''},</p>
                    <p>Ai solicitat un cod de verificare pentru autentificare în Sistemul de Vot Electronic.</p>
                    
                    <div class="code-box">
                        <p style="margin: 0 0 10px 0; color: #666;">Codul tău de verificare este:</p>
                        <div class="code">{code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Acest cod expiră în 10 minute</li>
                            <li>Nu partaja acest cod cu nimeni</li>
                            <li>Dacă nu ai solicitat acest cod, ignoră acest email</li>
                        </ul>
                    </div>
                    
                    <p>Introdu acest cod în formularul de autentificare pentru a completa login-ul.</p>
                </div>
                <div class="footer">
                    <p>Acest email a fost trimis automat. Te rugăm să nu răspunzi.</p>
                    <p>&copy; 2025 Sistem Vot Electronic - Republica Moldova</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Conținut text simplu (fallback)
        text_content = f"""
Cod de Verificare - Sistem Vot Electronic

Salut{(' ' + user_name) if user_name else ''},

Ai solicitat un cod de verificare pentru autentificare.

Codul tău de verificare este: {code}

IMPORTANT:
- Acest cod expiră în 10 minute
- Nu partaja acest cod cu nimeni
- Dacă nu ai solicitat acest cod, ignoră acest email

Introdu acest cod în formularul de autentificare pentru a completa login-ul.

---
Acest email a fost trimis automat. Te rugăm să nu răspunzi.
© 2025 Sistem Vot Electronic - Republica Moldova
        """
        
        # Adaugă ambele versiuni
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Trimite email-ul
        with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
        
        print(f"✅ Email trimis cu succes către {email}")
        return True
        
    except Exception as e:
        print(f"❌ Eroare la trimiterea email-ului către {email}: {e}")
        return False

