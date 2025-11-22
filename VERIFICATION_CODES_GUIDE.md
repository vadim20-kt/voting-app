# Ghid pentru Codurile de Verificare

## Cum funcționează sistemul de coduri

### 1. Generare și trimitere cod
- Când utilizatorul introduce IDNP și parolă corectă, se generează un cod de 6 cifre
- Utilizatorul alege metoda de trimitere: **Email** sau **SMS**
- Codul se salvează în baza de date în tabela `verification_codes`
- Codul expiră după **10 minute**

### 2. Verificare cod
- Utilizatorul introduce codul primit
- Sistemul verifică:
  - Codul există în baza de date
  - Codul nu a fost folosit deja
  - Codul nu a expirat (mai puțin de 10 minute)
- Dacă codul este valid, login-ul este completat

## Cum se testează codurile (în modul de dezvoltare)

### Metoda 1: Consola serverului Flask
1. Rulează serverul Flask
2. Încearcă să te loghezi
3. Verifică consola serverului - vei vedea:
   ```
   📧 Email trimis către user@example.com: Cod de verificare: 123456
   ```
   sau
   ```
   📱 SMS trimis către +373123456789: Cod de verificare: 123456
   ```

### Metoda 2: Consola browserului
1. Deschide Developer Tools (F12)
2. Mergi la tab-ul Console
3. După login, vei vedea codul în consolă:
   ```
   🔐 Cod de verificare (testare): 123456
   ```

### Metoda 3: Baza de date
1. Deschide phpMyAdmin
2. Selectează baza de date `voting_app`
3. Mergi la tabela `verification_codes`
4. Vei vedea codurile generate cu:
   - `idnp` - IDNP-ul utilizatorului
   - `code` - Codul de verificare
   - `used` - 0 (nefolosit) sau 1 (folosit)
   - `created_at` - Data și ora generării

## Pentru producție (trimitere reală)

### Email (SMTP)
Adaugă în `server/routes/auth_routes.py`:
```python
import smtplib
from email.mime.text import MIMEText

def send_verification_email(email, code):
    msg = MIMEText(f'Codul dvs. de verificare este: {code}')
    msg['Subject'] = 'Cod de verificare - Sistem Vot Electronic'
    msg['From'] = 'noreply@vote.md'
    msg['To'] = email
    
    # Configurare SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-password')
    server.send_message(msg)
    server.quit()
```

### SMS (API serviciu SMS)
Adaugă în `server/routes/auth_routes.py`:
```python
import requests

def send_verification_sms(telefon, code):
    # Exemplu cu Twilio sau alt serviciu SMS
    url = 'https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json'
    # Implementare trimitere SMS
    pass
```

## Structura tabelului verification_codes

```sql
CREATE TABLE verification_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idnp VARCHAR(13) NOT NULL,
    code VARCHAR(6) NOT NULL,
    used TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Verificare manuală în baza de date

```sql
-- Vezi toate codurile nefolosite
SELECT * FROM verification_codes WHERE used = 0;

-- Vezi codurile pentru un utilizator specific
SELECT * FROM verification_codes WHERE idnp = '1234567890123';

-- Șterge codurile expirate (mai vechi de 10 minute)
DELETE FROM verification_codes 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE);
```

