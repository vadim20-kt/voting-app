"""
Script de testare pentru trimiterea email-urilor
Rulează: python test_email.py
"""
import os
import sys

# Adaugă directorul părinte la path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Încarcă variabilele de mediu
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Variabile de mediu încărcate din .env")
except ImportError:
    print("⚠️ python-dotenv nu este instalat. Folosește variabile de mediu sistem.")
    print("   Instalează: pip install python-dotenv")

from utils.email_service import send_verification_email

def test_email():
    """Testează trimiterea unui email"""
    
    print("\n" + "="*50)
    print("TEST TRIMITERE EMAIL")
    print("="*50)
    
    # Verifică configurarea
    print("\n📋 Configurare SMTP:")
    print(f"   Host: {os.getenv('SMTP_HOST', 'LIPSĂ')}")
    print(f"   Port: {os.getenv('SMTP_PORT', 'LIPSĂ')}")
    print(f"   Username: {os.getenv('SMTP_USERNAME', 'LIPSĂ')}")
    print(f"   Password: {'✓ Setat' if os.getenv('SMTP_PASSWORD') else '❌ LIPSĂ'}")
    print(f"   From Email: {os.getenv('SMTP_FROM_EMAIL', 'LIPSĂ')}")
    
    # Verifică dacă este configurat
    if not os.getenv('SMTP_USERNAME') or not os.getenv('SMTP_PASSWORD'):
        print("\n❌ EROARE: SMTP nu este configurat!")
        print("\n📝 Pași pentru configurare:")
        print("   1. Creează fișierul server/.env")
        print("   2. Adaugă următoarele linii:")
        print("      SMTP_HOST=smtp.gmail.com")
        print("      SMTP_PORT=587")
        print("      SMTP_USERNAME=your-email@gmail.com")
        print("      SMTP_PASSWORD=your-app-password")
        print("      SMTP_FROM_EMAIL=your-email@gmail.com")
        print("      SMTP_FROM_NAME=Sistem Vot Electronic")
        print("\n   3. Pentru Gmail, folosește 'App Password':")
        print("      https://myaccount.google.com/apppasswords")
        return False
    
    # Solicită email de test
    print("\n" + "-"*50)
    test_email = input("Introdu email-ul pentru test (sau Enter pentru skip): ").strip()
    
    if not test_email:
        print("⏭️ Test omis")
        return False
    
    # Trimite email de test
    print(f"\n📧 Trimitere email către {test_email}...")
    test_code = "123456"
    
    try:
        result = send_verification_email(
            test_email,
            test_code,
            "Test User"
        )
        
        if result:
            print("✅ Email trimis cu succes!")
            print(f"   Verifică inbox-ul pentru cod: {test_code}")
            return True
        else:
            print("❌ Eroare la trimiterea email-ului")
            print("   Verifică consola pentru detalii")
            return False
            
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_email()

