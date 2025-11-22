# 🆓 Ghid: Publicare GRATUITĂ Online + Email/SMS Real

## 🎯 Opțiuni GRATUITE pentru Hosting

### ✅ Opțiunea 1: Render.com (RECOMANDAT - Cel mai simplu)

**Avantaje:**
- ✅ **100% GRATUIT** pentru aplicații web
- ✅ **MySQL gratuit** (PostgreSQL, dar putem adapta)
- ✅ **SSL automat** (HTTPS)
- ✅ **Deploy automat** din GitHub
- ✅ **Variabile de mediu** ușor de setat
- ✅ **Nu necesită CLI** - totul prin browser

**Limitări plan gratuit:**
- Aplicația se "adormește" după 15 minute de inactivitate
- Se "trezește" automat la primul request (poate dura 30-50 secunde)

#### Pași pentru Deploy pe Render:

**1. Creează cont:**
- Mergi la: https://render.com/
- Sign Up cu GitHub (recomandat) sau email

**2. Pregătește repository GitHub:**
```bash
cd c:\Users\admin\Desktop\voting-app
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/voting-app.git
git push -u origin main
```

**3. Creează Web Service:**
- Click "New" → "Web Service"
- Connect repository-ul tău
- Configurează:
  - **Name**: `voting-app-md`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `cd server && python app.py`
  - **Plan**: Free

**4. Creează PostgreSQL Database (gratuit):**
- Click "New" → "PostgreSQL"
- Name: `voting-app-db`
- Plan: Free
- Copiază "Internal Database URL"

**5. Configurează variabile de mediu:**
În Web Service → Environment:
```
DB_HOST=your-postgres-host
DB_USER=your-postgres-user
DB_PASSWORD=your-postgres-password
DB_NAME=your-postgres-db
DB_PORT=5432

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sistem Vot Electronic

SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

PORT=10000
```

**6. Deploy:**
- Click "Create Web Service"
- Render va face deploy automat
- Așteaptă 2-3 minute pentru build

**7. Obține URL-ul:**
- Aplicația va fi disponibilă la: `https://voting-app-md.onrender.com`

---

### ✅ Opțiunea 2: Railway.app (Foarte bun - $5 credit/lună gratuit)

**Avantaje:**
- ✅ **$5 credit gratuit/lună** (suficient pentru aplicație mică)
- ✅ **MySQL gratuit** inclus
- ✅ **SSL automat**
- ✅ **Deploy rapid**
- ✅ **Nu se "adormește"**

**Pași:**

**1. Creează cont:**
- Mergi la: https://railway.app/
- Sign Up cu GitHub

**2. Creează proiect:**
- Click "New Project"
- Selectează "Deploy from GitHub repo"
- Selectează repository-ul

**3. Adaugă MySQL:**
- Click "New" → "Database" → "MySQL"
- Se creează automat

**4. Configurează variabile de mediu:**
- Click pe Web Service → Variables
- Adaugă toate variabilele (email, SMS, etc.)

**5. Deploy automat:**
- Railway detectează automat Python
- Configurează build și start commands dacă e nevoie

---

### ✅ Opțiunea 3: PythonAnywhere (Specializat Python - GRATUIT)

**Avantaje:**
- ✅ **100% GRATUIT** pentru aplicații Python
- ✅ **MySQL gratuit** inclus
- ✅ **Nu se "adormește"**
- ✅ **Perfect pentru Flask**

**Limitări plan gratuit:**
- 1 aplicație web
- 512 MB storage
- 1 MySQL database

**Pași:**

**1. Creează cont:**
- Mergi la: https://www.pythonanywhere.com/
- Sign Up (gratuit)

**2. Upload codul:**
- Files → Upload files
- Sau folosește Git: `git clone https://github.com/your-username/voting-app.git`

**3. Configurează Web App:**
- Web → Add a new web app
- Selectează Flask
- Selectează Python 3.10
- Setează path-ul: `/home/yourusername/voting-app/server/app.py`

**4. Configurează MySQL:**
- Databases → Create database
- Se creează automat MySQL

**5. Configurează variabile de mediu:**
- Files → `.env` sau
- Web → WSGI configuration file → adaugă:
```python
import os
os.environ['SMTP_HOST'] = 'smtp.gmail.com'
os.environ['SMTP_USERNAME'] = 'your-email@gmail.com'
# ... etc
```

**6. Reload:**
- Web → Reload

---

### ✅ Opțiunea 4: Fly.io (Generos - GRATUIT)

**Avantaje:**
- ✅ **Plan gratuit generos**
- ✅ **3 VMs gratuite**
- ✅ **MySQL prin addon** (gratuit pentru început)

**Pași:**

**1. Instalează Fly CLI:**
```bash
# Windows: PowerShell
iwr https://fly.io/install.ps1 -useb | iex
```

**2. Login:**
```bash
fly auth login
```

**3. Creează aplicație:**
```bash
cd c:\Users\admin\Desktop\voting-app
fly launch
```

**4. Configurează MySQL:**
```bash
fly postgres create --name voting-app-db
fly postgres attach voting-app-db
```

**5. Deploy:**
```bash
fly deploy
```

---

### ✅ Opțiunea 5: Replit (Foarte simplu - GRATUIT)

**Avantaje:**
- ✅ **100% GRATUIT**
- ✅ **Editor online integrat**
- ✅ **Deploy cu un click**
- ✅ **Nu necesită Git**

**Pași:**

**1. Creează cont:**
- Mergi la: https://replit.com/
- Sign Up

**2. Creează Repl:**
- Click "Create Repl"
- Selectează "Python"
- Name: `voting-app`

**3. Upload fișierele:**
- Drag & drop sau copy-paste codul

**4. Configurează Secrets (variabile de mediu):**
- Click pe 🔒 icon (Secrets)
- Adaugă toate variabilele (SMTP, SMS, etc.)

**5. Deploy:**
- Click "Run"
- Replit va rula aplicația
- Obține URL-ul public

---

## 🎯 Recomandare Finală

**Pentru început (cel mai simplu):**
1. **Render.com** - cel mai ușor, totul prin browser
2. **PythonAnywhere** - perfect pentru Python/Flask

**Pentru producție:**
1. **Railway.app** - $5 credit/lună, nu se adormește
2. **Fly.io** - generos, dar necesită CLI

---

## 📧 Configurare Email Real (Gmail) - Aceeași pentru toate

**1. Obține App Password:**
- https://myaccount.google.com/apppasswords
- Generează parolă pentru "Mail" → "Other" → "Voting App"

**2. Configurează variabile de mediu:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Sistem Vot Electronic
```

---

## 📱 Configurare SMS Real (Twilio) - Aceeași pentru toate

**1. Creează cont Twilio:**
- https://www.twilio.com/
- Sign Up (gratuit, $15.50 credit)

**2. Configurează variabile de mediu:**
```
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

---

## 🔄 Adaptare pentru PostgreSQL (Render)

Dacă folosești Render cu PostgreSQL în loc de MySQL:

**1. Instalează psycopg2:**
```bash
pip install psycopg2-binary
```

**2. Actualizează `requirements.txt`:**
```
psycopg2-binary==2.9.9
```

**3. Modifică `server/utils/database.py`** să suporte PostgreSQL (dacă e nevoie)

---

## ✅ Checklist Deploy

- [ ] Am ales platforma (Render/PythonAnywhere/Railway)
- [ ] Am creat cont
- [ ] Am uploadat codul (GitHub sau direct)
- [ ] Am configurat baza de date
- [ ] Am setat variabilele de mediu pentru email
- [ ] Am setat variabilele de mediu pentru SMS
- [ ] Am făcut deploy
- [ ] Am testat login și primirea codului

---

## 🆘 Probleme?

**Aplicația nu pornește:**
- Verifică logs în dashboard-ul platformei
- Verifică că toate dependențele sunt în `requirements.txt`

**Email nu se trimite:**
- Verifică că folosești "App Password", nu parola normală
- Verifică logs pentru erori

**SMS nu se trimite:**
- Verifică că Twilio este configurat corect
- Verifică creditul Twilio

---

## 🎉 Rezultat

✅ Aplicația este online GRATUIT
✅ Email-urile se trimit real prin Gmail
✅ SMS-urile se trimit real prin Twilio
✅ Baza de date funcționează online

