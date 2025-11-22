# 🚀 Ghid Simplu: Deploy pe Render.com (GRATUIT)

## ⚡ Pași Rapizi (10 minute)

### Pasul 1: Creează Cont Render

1. Mergi la: https://render.com/
2. Click "Get Started for Free"
3. Sign Up cu GitHub (recomandat) sau email

### Pasul 2: Pregătește Codul pe GitHub

**Dacă nu ai GitHub:**

1. Creează cont: https://github.com/
2. Creează repository nou: "voting-app"
3. Upload codul:

**În terminal:**
```bash
cd c:\Users\admin\Desktop\voting-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/voting-app.git
git push -u origin main
```

**Sau folosește GitHub Desktop:**
- Download: https://desktop.github.com/
- Add repository → Selectează folderul `voting-app`
- Publish repository

### Pasul 3: Creează Web Service pe Render

1. **Login în Render**
2. Click **"New"** → **"Web Service"**
3. **Connect GitHub** (dacă nu ai conectat deja)
4. **Selectează repository-ul** `voting-app`
5. **Configurează:**
   - **Name**: `voting-app-md`
   - **Environment**: `Python 3`
   - **Region**: Cel mai apropiat de tine
   - **Branch**: `main`
   - **Root Directory**: (lasă gol)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd server && python app.py`
   - **Plan**: **Free**

6. Click **"Create Web Service"**

### Pasul 4: Creează PostgreSQL Database

1. Click **"New"** → **"PostgreSQL"**
2. **Name**: `voting-app-db`
3. **Database**: `voting_app`
4. **User**: (se generează automat)
5. **Region**: Același ca Web Service
6. **Plan**: **Free**
7. Click **"Create Database"**
8. **Copiază "Internal Database URL"** (va arăta: `postgresql://user:pass@host:5432/dbname`)

### Pasul 5: Configurează Variabile de Mediu

În Web Service → **Environment** → **Add Environment Variable**:

**Baza de date (din PostgreSQL URL):**
```
DB_HOST=dpg-xxxxx-a.oregon-postgres.render.com
DB_USER=voting_app_user
DB_PASSWORD=your_password
DB_NAME=voting_app
DB_PORT=5432
```

**Email (Gmail):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sistem Vot Electronic
```

**SMS (Twilio):**
```
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

**Port (obligatoriu pentru Render):**
```
PORT=10000
```

### Pasul 6: Obține App Password Gmail

1. Mergi la: https://myaccount.google.com/apppasswords
2. Generează parolă pentru "Mail" → "Other" → "Voting App"
3. Copiază parola (16 caractere)
4. Adaugă în variabilele de mediu ca `SMTP_PASSWORD`

### Pasul 7: Configurează Twilio (SMS)

1. Creează cont: https://www.twilio.com/ (gratuit, $15.50 credit)
2. Obține: Account SID, Auth Token, Număr de telefon
3. Adaugă în variabilele de mediu

### Pasul 8: Așteaptă Deploy

- Render va face build automat
- Așteaptă 2-3 minute
- Vei vedea progress în dashboard

### Pasul 9: Obține URL-ul

- După deploy, aplicația va fi la: `https://voting-app-md.onrender.com`
- Click pe URL pentru a deschide

### Pasul 10: Inițializează Baza de Date

**Opțiunea A: Prin Shell (Recomandat)**
1. În Render → Web Service → **Shell**
2. Rulează:
```bash
cd server
python -c "from utils.database import init_db; init_db()"
```

**Opțiunea B: Prin cod**
- Adaugă în `server/app.py` să ruleze `init_db()` automat la primul start

---

## ✅ Verificare

1. **Deschide aplicația**: `https://voting-app-md.onrender.com`
2. **Testează înregistrare** - creează un cont
3. **Testează login cu email** - verifică inbox-ul Gmail
4. **Testează login cu SMS** - verifică telefonul

---

## 🔧 Comenzi Utile

**Vezi logs:**
- Render → Web Service → **Logs**

**Redeploy:**
- Render → Web Service → **Manual Deploy**

**Actualizează codul:**
```bash
git add .
git commit -m "Update"
git push origin main
```
(Render va redeploy automat)

---

## ⚠️ Notă Importantă

**Planul Free de la Render:**
- Aplicația se "adormește" după 15 minute de inactivitate
- Se "trezește" automat la primul request (poate dura 30-50 secunde)
- Pentru producție, consideră upgrade la plan plătit ($7/lună)

---

## 🎉 Gata!

Aplicația ta este online GRATUIT și funcționează cu email și SMS real! 🚀

