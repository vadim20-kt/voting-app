from flask import Blueprint, request, jsonify
from utils.database import get_db_connection, generate_verification_code
import hashlib
import traceback

# Importă serviciile cu gestionare de erori
try:
    from utils.email_service import send_verification_email
except Exception as e:
    print(f"⚠️ Eroare la importarea email_service: {e}")
    traceback.print_exc()
    def send_verification_email(*args, **kwargs):
        print("📧 Email service nu este disponibil - afișează cod în consolă")
        return False

try:
    from utils.sms_service import send_verification_sms
except Exception as e:
    print(f"⚠️ Eroare la importarea sms_service: {e}")
    traceback.print_exc()
    def send_verification_sms(*args, **kwargs):
        print("📱 SMS service nu este disponibil - afișează cod în consolă")
        return False

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        idnp = data.get('idnp')
        parola = data.get('parola')

        if not idnp or not parola:
            return jsonify({'success': False, 'error': 'IDNP și parola sunt obligatorii'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Eroare de conexiune la baza de date'}), 500
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE idnp = %s", (idnp,))
        user = cursor.fetchone()

        if user:
            # Verifică parola
            hashed_password = hashlib.md5(parola.encode()).hexdigest()
            if hashed_password == user['parola']:
                # Verifică dacă este cerut cod de verificare
                verification_code = data.get('verification_code')
                
                if verification_code:
                    # Verifică codul de verificare
                    cursor.execute(
                        "SELECT * FROM verification_codes WHERE idnp = %s AND code = %s AND used = 0 AND created_at > DATE_SUB(NOW(), INTERVAL 10 MINUTE)",
                        (idnp, verification_code)
                    )
                    verification = cursor.fetchone()
                    
                    if not verification:
                        return jsonify({
                            'success': False, 
                            'error': 'Cod de verificare invalid sau expirat',
                            'requires_verification': True
                        }), 401
                    
                    # Marchează codul ca folosit
                    cursor.execute(
                        "UPDATE verification_codes SET used = 1 WHERE id = %s",
                        (verification['id'],)
                    )
                    conn.commit()
                else:
                    # Generează și trimite cod de verificare
                    verification_method = data.get('verification_method', 'email')  # email sau telefon
                    code = generate_verification_code()
                    
                    # Șterge codurile vechi pentru acest utilizator
                    cursor.execute("DELETE FROM verification_codes WHERE idnp = %s", (idnp,))
                    
                    # Salvează codul nou
                    cursor.execute(
                        "INSERT INTO verification_codes (idnp, code) VALUES (%s, %s)",
                        (idnp, code)
                    )
                    conn.commit()
                    
                    # Trimite codul prin metoda selectată
                    message = ''
                    email_sent = False
                    sms_sent = False
                    
                    try:
                        if verification_method == 'email' and user.get('email'):
                            email_sent = send_verification_email(
                                user['email'], 
                                code, 
                                user.get('nume')
                            )
                            if email_sent:
                                message = f'Cod de verificare trimis la email: {user["email"]}'
                            else:
                                message = 'Eroare la trimiterea email-ului. Verifică consola serverului pentru cod.'
                                print(f"📧 Cod de verificare pentru {user['email']}: {code}")
                        elif verification_method == 'telefon' and user.get('telefon'):
                            sms_sent = send_verification_sms(
                                user['telefon'], 
                                code, 
                                user.get('nume')
                            )
                            if sms_sent:
                                message = f'Cod de verificare trimis la telefon: {user["telefon"]}'
                            else:
                                message = 'Eroare la trimiterea SMS-ului. Verifică consola serverului pentru cod.'
                                print(f"📱 Cod de verificare pentru {user['telefon']}: {code}")
                        else:
                            # Fallback - afișează în consolă
                            print(f"🔐 Cod de verificare pentru {user['nume']} ({idnp}): {code}")
                            if user.get('email'):
                                print(f"   Email: {user['email']}")
                            if user.get('telefon'):
                                print(f"   Telefon: {user['telefon']}")
                            message = 'Cod de verificare generat. Verifică consola serverului pentru cod.'
                    except Exception as send_error:
                        # Dacă trimiterea eșuează, totuși returnează codul pentru testare
                        print(f"⚠️ Eroare la trimiterea codului: {send_error}")
                        print(f"🔐 Cod de verificare pentru {user['nume']} ({idnp}): {code}")
                        message = 'Eroare la trimiterea codului. Verifică consola serverului pentru cod.'
                    
                    return jsonify({
                        'success': False,
                        'requires_verification': True,
                        'message': message,
                        'verification_method': verification_method
                        # Nu returnăm codul în răspuns - doar în consola serverului
                    }), 200
                
                # Dacă codul este valid sau nu este necesar, continuă cu login-ul
                # Obține adresa IP a utilizatorului
                ip_address = request.remote_addr
                if request.headers.get('X-Forwarded-For'):
                    ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
                
                # Salvează datele de login în baza de date
                try:
                    cursor.execute('''
                        INSERT INTO login_logs (user_id, idnp, nume, email, ip_address, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        user['id'],
                        user['idnp'],
                        user['nume'],
                        user['email'],
                        ip_address,
                        'success'
                    ))
                    conn.commit()
                except Exception as log_error:
                    print(f"Eroare la salvarea logului de login: {log_error}")
                    # Continuă chiar dacă logarea eșuează
                
                user_data = {
                    'id': user['id'],
                    'idnp': user['idnp'],
                    'nume': user['nume'],
                    'email': user['email'],
                    'is_admin': bool(user['is_admin'])
                }
                return jsonify({'success': True, 'user': user_data})
            else:
                # Salvează și încercările eșuate de login
                try:
                    ip_address = request.remote_addr
                    if request.headers.get('X-Forwarded-For'):
                        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
                    
                    cursor.execute('''
                        INSERT INTO login_logs (user_id, idnp, nume, email, ip_address, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        user['id'],
                        user['idnp'],
                        user['nume'],
                        user['email'],
                        ip_address,
                        'failed_password'
                    ))
                    conn.commit()
                except Exception as log_error:
                    print(f"Eroare la salvarea logului de login: {log_error}")
                
                return jsonify({'success': False, 'error': 'IDNP sau parolă incorectă'}), 401
        else:
            # Salvează încercările de login pentru utilizatori inexistenți
            try:
                ip_address = request.remote_addr
                if request.headers.get('X-Forwarded-For'):
                    ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
                
                cursor.execute('''
                    INSERT INTO login_logs (user_id, idnp, ip_address, status)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    None,
                    idnp,
                    ip_address,
                    'failed_user_not_found'
                ))
                conn.commit()
            except Exception as log_error:
                print(f"Eroare la salvarea logului de login: {log_error}")
            
            return jsonify({'success': False, 'error': 'Utilizatorul nu există'}), 404

    except Exception as e:
        print(f"❌ Eroare în login: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Eroare la autentificare: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        idnp = data.get('idnp')
        nume = data.get('nume')
        email = data.get('email')
        telefon = data.get('telefon')
        parola = data.get('parola')

        # Validări
        if not all([idnp, nume, parola]):
            return jsonify({'success': False, 'error': 'IDNP, nume și parola sunt obligatorii'}), 400

        if not idnp.isdigit() or len(idnp) != 13:
            return jsonify({'success': False, 'error': 'IDNP trebuie să aibă exact 13 cifre'}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Eroare de conexiune la baza de date'}), 500
            
        cursor = conn.cursor(dictionary=True)

        # Verifică dacă IDNP-ul există deja
        cursor.execute("SELECT id FROM users WHERE idnp = %s", (idnp,))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'IDNP-ul există deja în sistem'}), 400

        # Hash-uieste parola
        hashed_password = hashlib.md5(parola.encode()).hexdigest()

        # Inserează utilizatorul nou
        cursor.execute(
            "INSERT INTO users (idnp, nume, email, telefon, parola) VALUES (%s, %s, %s, %s, %s)",
            (idnp, nume, email, telefon, hashed_password)
        )
        conn.commit()

        return jsonify({'success': True, 'message': 'Cont creat cu succes! Vă puteți autentifica acum.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@auth_bp.route('/request-code', methods=['POST'])
def request_verification_code():
    try:
        data = request.get_json()
        idnp = data.get('idnp')
        verification_method = data.get('verification_method', 'email')  # email sau telefon
        
        if not idnp:
            return jsonify({'success': False, 'error': 'IDNP este obligatoriu'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă utilizatorul există și obține datele
        cursor.execute("SELECT id, nume, email, telefon FROM users WHERE idnp = %s", (idnp,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': 'Utilizatorul nu există'}), 404
        
        # Verifică dacă metoda selectată este disponibilă
        if verification_method == 'email' and not user.get('email'):
            return jsonify({'success': False, 'error': 'Email-ul nu este înregistrat pentru acest utilizator'}), 400
        if verification_method == 'telefon' and not user.get('telefon'):
            return jsonify({'success': False, 'error': 'Numărul de telefon nu este înregistrat pentru acest utilizator'}), 400
        
        # Generează cod nou
        code = generate_verification_code()
        
        # Șterge codurile vechi și expirate
        cursor.execute("DELETE FROM verification_codes WHERE idnp = %s OR created_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE)", (idnp,))
        
        # Salvează codul nou
        cursor.execute(
            "INSERT INTO verification_codes (idnp, code) VALUES (%s, %s)",
            (idnp, code)
        )
        conn.commit()
        
        # Trimite codul prin metoda selectată
        message = ''
        email_sent = False
        sms_sent = False
        
        try:
            if verification_method == 'email' and user.get('email'):
                email_sent = send_verification_email(
                    user['email'], 
                    code, 
                    user.get('nume')
                )
                if email_sent:
                    message = f'Cod de verificare trimis la email: {user["email"]}'
                else:
                    message = 'Eroare la trimiterea email-ului. Verifică consola serverului pentru cod.'
                    print(f"📧 Cod de verificare pentru {user['email']}: {code}")
            elif verification_method == 'telefon' and user.get('telefon'):
                sms_sent = send_verification_sms(
                    user['telefon'], 
                    code, 
                    user.get('nume')
                )
                if sms_sent:
                    message = f'Cod de verificare trimis la telefon: {user["telefon"]}'
                else:
                    message = 'Eroare la trimiterea SMS-ului. Verifică consola serverului pentru cod.'
                    print(f"📱 Cod de verificare pentru {user['telefon']}: {code}")
            else:
                print(f"🔐 Cod de verificare pentru {user['nume']} ({idnp}): {code}")
                message = 'Cod de verificare generat. Verifică consola serverului pentru cod.'
        except Exception as send_error:
            # Dacă trimiterea eșuează, totuși returnează codul pentru testare
            print(f"⚠️ Eroare la trimiterea codului: {send_error}")
            print(f"🔐 Cod de verificare pentru {user['nume']} ({idnp}): {code}")
            message = 'Eroare la trimiterea codului. Verifică consola serverului pentru cod.'
        
        return jsonify({
            'success': True, 
            'message': message,
            'verification_method': verification_method
            # Nu returnăm codul în răspuns - doar în consola serverului
        })
        
    except Exception as e:
        print(f"❌ Eroare request code: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Eroare la solicitarea codului: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    try:
        data = request.get_json()
        idnp = data.get('idnp')
        code = data.get('code')
        
        if not idnp or not code:
            return jsonify({'success': False, 'error': 'IDNP și codul sunt obligatorii'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică codul
        cursor.execute(
            "SELECT * FROM verification_codes WHERE idnp = %s AND code = %s AND used = 0",
            (idnp, code)
        )
        verification = cursor.fetchone()
        
        if verification:
            # Marchează codul ca folosit
            cursor.execute(
                "UPDATE verification_codes SET used = 1 WHERE id = %s",
                (verification['id'],)
            )
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Cod verificat cu succes'})
        else:
            return jsonify({'success': False, 'error': 'Cod invalid sau expirat'}), 401
        
    except Exception as e:
        print(f"❌ Eroare în verify_code: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Eroare la verificarea codului: {str(e)}'}), 500
    finally:
        if 'conn' in locals():
            conn.close()