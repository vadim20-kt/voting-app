# Configurare Email și SMS pentru Coduri de Verificare

## 📧 Configurare Email (SMTP)

### Opțiunea 1: Gmail

1. **Activează "App Password" pentru Gmail:**
   - Mergi la: https://myaccount.google.com/apppasswords
   - Selectează "Mail" și "Other (Custom name)"
   - Introdu "Voting App"
   - Copiază parola generată (16 caractere)

2. **Configurează variabilele de mediu:**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_FROM_EMAIL=noreply@vote.md
   SMTP_FROM_NAME=Sistem Vot Electronic
   ```

### Opțiunea 2: Alt serviciu SMTP

**Outlook/Hotmail:**
```
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo:**
```
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
```

**Serviciu SMTP propriu:**
```
SMTP_HOST=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## 📱 Configurare SMS

### Opțiunea 1: Twilio (Recomandat)

1. **Creează cont Twilio:**
   - Mergi la: https://www.twilio.com/
   - Înregistrează-te și obține un număr de telefon

2. **Obține credențialele:**
   - Account SID
   - Auth Token
   - Număr de telefon (From Number)

3. **Configurează variabilele de mediu:**
   ```bash
   SMS_PROVIDER=twilio
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_NUMBER=+1234567890
   ```

### Opțiunea 2: SMS Gateway

1. **Alege un provider SMS Gateway:**
   - SMS Gateway API
   - Nexmo/Vonage
   - Alt serviciu SMS

2. **Configurează:**
   ```bash
   SMS_PROVIDER=sms_gateway
   SMS_GATEWAY_URL=https://api.smsgateway.com/send
   SMS_GATEWAY_API_KEY=your_api_key
   ```

## 🚀 Cum se activează

### Pasul 1: Instalează dependențele

```bash
pip install -r requirements.txt
```

Sau manual:
```bash
pip install python-dotenv requests
```

### Pasul 2: Configurează variabilele de mediu

**Opțiunea A: Fișier .env (Recomandat pentru dezvoltare)**

1. Creează fișierul `.env` în folderul `server/`:
   ```bash
   cd server
   # Windows:
   copy .env.example .env
   # Linux/Mac:
   cp .env.example .env
   ```

2. Editează `.env` și completează credențialele:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

**Opțiunea B: Variabile de mediu sistem (Recomandat pentru producție)**

Windows PowerShell:
```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_USERNAME="your-email@gmail.com"
$env:SMTP_PASSWORD="your-password"
```

Linux/Mac:
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-password
```

### Metoda 2: Configurare directă în cod

Editează `server/utils/email_service.py` și `server/utils/sms_service.py`:
```python
SMTP_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    # ...
}
```

## ✅ Testare

### Test Email:
1. Configurează SMTP
2. Încearcă să te loghezi
3. Verifică inbox-ul pentru email cu cod

### Test SMS:
1. Configurează Twilio sau SMS Gateway
2. Încearcă să te loghezi
3. Verifică telefonul pentru SMS cu cod

## 🔒 Securitate

- **NU comite** fișierul `.env` în git!
- Folosește "App Passwords" pentru Gmail, nu parola principală
- Păstrează credențialele în siguranță
- Folosește variabile de mediu în producție

## 📝 Notă

Dacă nu configurezi email/SMS, codurile vor fi afișate doar în consolă pentru testare.

