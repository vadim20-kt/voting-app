"""
Script de testare pentru trimiterea SMS-urilor
Rulează: python test_sms.py
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

from utils.sms_service import send_verification_sms

def test_sms():
    """Testează trimiterea unui SMS"""
    
    print("\n" + "="*50)
    print("TEST TRIMITERE SMS")
    print("="*50)
    
    # Verifică configurarea
    print("\n📋 Configurare SMS:")
    print(f"   Provider: {os.getenv('SMS_PROVIDER', 'LIPSĂ')}")
    
    if os.getenv('SMS_PROVIDER') == 'twilio':
        print(f"   Twilio Account SID: {os.getenv('TWILIO_ACCOUNT_SID', 'LIPSĂ')}")
        print(f"   Twilio Auth Token: {'✓ Setat' if os.getenv('TWILIO_AUTH_TOKEN') else '❌ LIPSĂ'}")
        print(f"   From Number: {os.getenv('TWILIO_FROM_NUMBER', 'LIPSĂ')}")
    else:
        print(f"   SMS Gateway URL: {os.getenv('SMS_GATEWAY_URL', 'LIPSĂ')}")
        print(f"   API Key: {'✓ Setat' if os.getenv('SMS_GATEWAY_API_KEY') else '❌ LIPSĂ'}")
    
    # Verifică dacă este configurat
    provider = os.getenv('SMS_PROVIDER', 'twilio')
    if provider == 'twilio':
        if not os.getenv('TWILIO_ACCOUNT_SID') or not os.getenv('TWILIO_AUTH_TOKEN'):
            print("\n❌ EROARE: Twilio nu este configurat!")
            print("\n📝 Pași pentru configurare:")
            print("   1. Creează cont Twilio: https://www.twilio.com/")
            print("   2. Obține Account SID, Auth Token și număr de telefon")
            print("   3. Adaugă în server/.env:")
            print("      SMS_PROVIDER=twilio")
            print("      TWILIO_ACCOUNT_SID=your_account_sid")
            print("      TWILIO_AUTH_TOKEN=your_auth_token")
            print("      TWILIO_FROM_NUMBER=+1234567890")
            return False
    
    # Solicită telefon de test
    print("\n" + "-"*50)
    test_phone = input("Introdu numărul de telefon pentru test (format: +373XXXXXXXXX sau Enter pentru skip): ").strip()
    
    if not test_phone:
        print("⏭️ Test omis")
        return False
    
    # Trimite SMS de test
    print(f"\n📱 Trimitere SMS către {test_phone}...")
    test_code = "123456"
    
    try:
        result = send_verification_sms(
            test_phone,
            test_code,
            "Test User"
        )
        
        if result:
            print("✅ SMS trimis cu succes!")
            print(f"   Verifică telefonul pentru cod: {test_code}")
            return True
        else:
            print("❌ Eroare la trimiterea SMS-ului")
            print("   Verifică consola pentru detalii")
            return False
            
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_sms()

