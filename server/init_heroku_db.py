"""
Script pentru inițializarea bazei de date pe Heroku
Rulează: heroku run python server/init_heroku_db.py
"""
import sys
import os

# Adaugă path-ul corect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import init_db

if __name__ == '__main__':
    print("="*50)
    print("INITIALIZARE BAZA DE DATE HEROKU")
    print("="*50)
    
    print("\n📊 Inițializare tabele...")
    init_db()
    
    print("\n✅ Baza de date inițializată cu succes!")
    print("\n📝 Următorii pași:")
    print("   1. Creează un cont admin prin interfața de înregistrare")
    print("   2. Sau adaugă manual utilizatori în baza de date")
    print("   3. Testează login cu email/SMS real")

