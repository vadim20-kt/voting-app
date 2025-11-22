# 🚀 Ghid Rapid: Publicare Online + Email/SMS Real

## ⚡ Soluție Rapidă (15 minute)

### Pasul 1: Instalează Heroku CLI

**Windows:**
1. Descarcă: https://devcenter.heroku.com/articles/heroku-cli
2. Instalează și repornește terminalul
3. Verifică: `heroku --version`

### Pasul 2: Login Heroku

```bash
heroku login
```
(Se deschide browser pentru login - creează cont dacă nu ai)

### Pasul 3: Creează Aplicație

```bash
cd c:\Users\admin\Desktop\voting-app
heroku create voting-app-md
```

### Pasul 4: Adaugă Baza de Date MySQL

```bash
heroku addons:create cleardb:ignite
```

### Pasul 5: Configurează Email (Gmail)

**1. Obține App Password Gmail:**
- Mergi la: https://myaccount.google.com/apppasswords
- Generează parolă pentru "Mail" → "Other" → "Voting App"
- Copiază parola (16 caractere)

**2. Configurează în Heroku:**
```bash
heroku config:set SMTP_HOST=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=your-email@gmail.com
heroku config:set SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
heroku config:set SMTP_FROM_EMAIL=your-email@gmail.com
heroku config:set SMTP_FROM_NAME="Sistem Vot Electronic"
```

**Înlocuiește:**
- `your-email@gmail.com` cu adresa ta de Gmail
- `xxxx-xxxx-xxxx-xxxx` cu parola de aplicație generată

### Pasul 6: Configurează SMS (Twilio)

**1. Creează cont Twilio:**
- Mergi la: https://www.twilio.com/
- Sign Up (gratuit, primești $15.50 credit)
- Obține: Account SID, Auth Token, Număr de telefon

**2. Configurează în Heroku:**
```bash
heroku config:set SMS_PROVIDER=twilio
heroku config:set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
heroku config:set TWILIO_AUTH_TOKEN=your_auth_token
heroku config:set TWILIO_FROM_NUMBER=+1234567890
```

### Pasul 7: Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Pasul 8: Inițializează Baza de Date

```bash
heroku run python server/init_heroku_db.py
```

Aceasta va crea toate tabelele necesare în baza de date.

### Pasul 9: Verifică

```bash
heroku open
```

Aplicația este online! 🎉

---

## ✅ Verificare Funcționare

### Test Email:
1. Mergi pe aplicația online
2. Încearcă login
3. Alege metoda "Email"
4. Verifică inbox-ul Gmail pentru cod

### Test SMS:
1. Mergi pe aplicația online
2. Încearcă login
3. Alege metoda "SMS"
4. Verifică telefonul pentru SMS

---

## 🔧 Comenzi Utile

**Vezi logs:**
```bash
heroku logs --tail
```

**Verifică configurarea:**
```bash
heroku config
```

**Actualizează aplicația:**
```bash
git add .
git commit -m "Update"
git push heroku main
```

**Deschide aplicația:**
```bash
heroku open
```

---

## 📝 Notă Importantă

După deploy, trebuie să:
1. **Inițializezi baza de date** - rulează `init_db()` o dată
2. **Creezi utilizatori** - prin interfața de înregistrare
3. **Testezi login** - cu email și SMS real

---

## 🆘 Probleme?

**Aplicația nu pornește:**
```bash
heroku logs --tail
```

**Email nu se trimite:**
- Verifică că folosești "App Password", nu parola normală
- Verifică logs pentru erori

**SMS nu se trimite:**
- Verifică că Twilio este configurat corect
- Verifică creditul Twilio în dashboard

---

## 🎯 Rezultat Final

✅ Aplicația este online și accesibilă de oriunde
✅ Email-urile se trimit real prin Gmail
✅ SMS-urile se trimit real prin Twilio
✅ Baza de date MySQL funcționează online

