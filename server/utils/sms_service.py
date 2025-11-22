"""
Serviciu pentru trimiterea SMS-urilor cu coduri de verificare
Suportă multiple provideri: Twilio, SMS Gateway, etc.
"""
import requests
import os

# Încearcă să încarce dotenv dacă este disponibil
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv nu este instalat, folosește variabilele de mediu sistem

# Configurare SMS (din variabile de mediu sau valori default)
SMS_CONFIG = {
    'provider': os.getenv('SMS_PROVIDER', 'twilio'),  # twilio, sms_gateway, etc.
    'twilio_account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
    'twilio_auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
    'twilio_from_number': os.getenv('TWILIO_FROM_NUMBER', ''),
    'sms_gateway_url': os.getenv('SMS_GATEWAY_URL', ''),
    'sms_gateway_api_key': os.getenv('SMS_GATEWAY_API_KEY', ''),
}

def send_verification_sms(telefon, code, user_name=None):
    """
    Trimite codul de verificare prin SMS
    
    Args:
        telefon: Numărul de telefon (format internațional: +373XXXXXXXXX)
        code: Codul de verificare (6 cifre)
        user_name: Numele utilizatorului (opțional)
    
    Returns:
        bool: True dacă SMS-ul a fost trimis cu succes, False altfel
    """
    try:
        # Normalizează numărul de telefon
        telefon = telefon.strip()
        if not telefon.startswith('+'):
            # Adaugă prefixul pentru Moldova dacă lipsește
            if telefon.startswith('0'):
                telefon = '+373' + telefon[1:]
            else:
                telefon = '+373' + telefon
        
        provider = SMS_CONFIG['provider']
        
        if provider == 'twilio':
            return _send_via_twilio(telefon, code, user_name)
        elif provider == 'sms_gateway':
            return _send_via_sms_gateway(telefon, code, user_name)
        else:
            print(f"⚠️ Provider SMS necunoscut: {provider}. Cod pentru {telefon}: {code}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare la trimiterea SMS-ului către {telefon}: {e}")
        return False

def _send_via_twilio(telefon, code, user_name=None):
    """Trimite SMS folosind Twilio API"""
    try:
        account_sid = SMS_CONFIG['twilio_account_sid']
        auth_token = SMS_CONFIG['twilio_auth_token']
        from_number = SMS_CONFIG['twilio_from_number']
        
        if not all([account_sid, auth_token, from_number]):
            print(f"⚠️ Twilio nu este configurat. Cod pentru {telefon}: {code}")
            return False
        
        message = f"Cod de verificare: {code}. Expiră în 10 minute. Nu partaja acest cod."
        if user_name:
            message = f"Salut {user_name}, {message}"
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        data = {
            'From': from_number,
            'To': telefon,
            'Body': message
        }
        
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        
        if response.status_code == 201:
            print(f"✅ SMS trimis cu succes către {telefon} (Twilio)")
            return True
        else:
            print(f"❌ Eroare Twilio: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare Twilio: {e}")
        return False

def _send_via_sms_gateway(telefon, code, user_name=None):
    """Trimite SMS folosind un SMS Gateway generic"""
    try:
        gateway_url = SMS_CONFIG['sms_gateway_url']
        api_key = SMS_CONFIG['sms_gateway_api_key']
        
        if not gateway_url or not api_key:
            print(f"⚠️ SMS Gateway nu este configurat. Cod pentru {telefon}: {code}")
            return False
        
        message = f"Cod de verificare: {code}. Expiră în 10 minute."
        if user_name:
            message = f"Salut {user_name}, {message}"
        
        payload = {
            'api_key': api_key,
            'to': telefon,
            'message': message
        }
        
        response = requests.post(gateway_url, json=payload)
        
        if response.status_code == 200:
            print(f"✅ SMS trimis cu succes către {telefon} (SMS Gateway)")
            return True
        else:
            print(f"❌ Eroare SMS Gateway: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Eroare SMS Gateway: {e}")
        return False

