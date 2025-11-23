from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import hashlib
from datetime import datetime

# Încarcă variabilele de mediu
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Variabile de mediu încărcate")
except ImportError:
    print("⚠️ python-dotenv nu este instalat")

app = Flask(__name__)
CORS(app)

# Configurație bază de date - URL-ul tău direct
DATABASE_URL = "postgresql://voting_app_ldec_user:VROdX2znIac3Hk7TRE2Xzgb18axGRwqx@dpg-d4h4rvh5pdvs7390tdrg-a.frankfurt-postgres.render.com:5432/voting_app_ldec"

print(f"🔗 Conectare la: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

# Creează engine și sesiune
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print("✅ Engine baza de date creat")
except Exception as e:
    print(f"❌ Eroare creare engine: {e}")
    engine = None
    SessionLocal = None

# Funcție hash pentru parole
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Funcție pentru inițializare baza de date
def init_db():
    if not engine:
        print("❌ Nu se poate inițializa - engine negăsit")
        return
        
    try:
        with engine.connect() as conn:
            # Verifică dacă coloana idnp există deja
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'idnp'
            """))
            
            if not result.fetchone():
                # Adaugă coloana idnp dacă nu există
                conn.execute(text("ALTER TABLE users ADD COLUMN idnp VARCHAR(13)"))
                print("✅ Coloana idnp adăugată în tabela users")
            
            # Creează toate tabelele necesare
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    idnp VARCHAR(13) UNIQUE,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password VARCHAR(200) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS rezultate (
                    id SERIAL PRIMARY KEY,
                    nume_candidat VARCHAR(100) NOT NULL,
                    partid VARCHAR(100),
                    numar_voturi INTEGER DEFAULT 0,
                    data_actualizare TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS noutati (
                    id SERIAL PRIMARY KEY,
                    titlu VARCHAR(200) NOT NULL,
                    continut TEXT,
                    data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS login_logs (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    idnp VARCHAR(13),
                    ip_address VARCHAR(45),
                    success BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS voturi (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    candidat_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Adaugă date demo
            # Verifică dacă adminul există
            admin_check = conn.execute(text("SELECT * FROM users WHERE username = 'admin'"))
            if not admin_check.fetchone():
                conn.execute(text("""
                    INSERT INTO users (username, email, password, idnp, is_admin) 
                    VALUES ('admin', 'admin@voting.com', %s, '1234567890123', TRUE)
                """), (hash_password('admin123'),))
                print("✅ Cont admin creat")
            
            # Adaugă candidați demo
            candidati_check = conn.execute(text("SELECT * FROM rezultate"))
            if not candidati_check.fetchone():
                conn.execute(text("""
                    INSERT INTO rezultate (nume_candidat, partid, numar_voturi) 
                    VALUES 
                    ('Ion Popescu', 'Partidul Democrat', 0),
                    ('Maria Ionescu', 'Partidul Liberal', 0),
                    ('Vasile Georgescu', 'Partidul Social', 0)
                """))
                print("✅ Candidați demo adăugați")
            
            # Adaugă știri demo
            noutati_check = conn.execute(text("SELECT * FROM noutati"))
            if not noutati_check.fetchone():
                conn.execute(text("""
                    INSERT INTO noutati (titlu, continut) 
                    VALUES 
                    ('Alegeri 2024', 'Procesul electoral a început. Toți cetățenii sunt invitați să voteze.'),
                    ('Informații importante', 'Vă rugăm să vă aduceți buletinul la secția de votare.')
                """))
                print("✅ Știri demo adăugate")
            
            print("✅ Toate tabelele verificate/create cu date demo")
    except Exception as e:
        print(f"❌ Eroare inițializare baza date: {e}")

# Inițializează baza de date
try:
    print("🌐 Inițializare baza de date...")
    init_db()
    print("✅ Baza de date inițializată")
except Exception as e:
    print(f"⚠️ Avertisment inițializare baza date: {e}")

# Configurare fișiere statice
app.static_folder = '../client'
app.static_url_path = ''

# Rute pentru autentificare
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username și parolă sunt obligatorii'}), 400
        
        with SessionLocal() as db:
            # Caută utilizatorul
            user = db.execute(text("""
                SELECT * FROM users WHERE username = :username OR email = :username
            """), {'username': username}).fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'Utilizatorul nu există'}), 401
            
            # Verifică parola
            hashed_password = hash_password(password)
            if user.password != hashed_password:
                return jsonify({'success': False, 'message': 'Parolă incorectă'}), 401
            
            # Loghează accesul
            db.execute(text("""
                INSERT INTO login_logs (user_id, idnp, ip_address, success) 
                VALUES (:user_id, :idnp, :ip, TRUE)
            """), {
                'user_id': user.id,
                'idnp': user.idnp,
                'ip': request.remote_addr
            })
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Login reușit',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la login: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        idnp = data.get('idnp')
        password = data.get('password')
        
        if not all([username, email, idnp, password]):
            return jsonify({'success': False, 'message': 'Toate câmpurile sunt obligatorii'}), 400
        
        with SessionLocal() as db:
            # Verifică dacă username/email/idnp există deja
            existing_user = db.execute(text("""
                SELECT * FROM users WHERE username = :username OR email = :email OR idnp = :idnp
            """), {'username': username, 'email': email, 'idnp': idnp}).fetchone()
            
            if existing_user:
                return jsonify({'success': False, 'message': 'Username, email sau IDNP există deja'}), 400
            
            # Creează utilizatorul nou
            hashed_password = hash_password(password)
            db.execute(text("""
                INSERT INTO users (username, email, idnp, password) 
                VALUES (:username, :email, :idnp, :password)
            """), {
                'username': username,
                'email': email,
                'idnp': idnp,
                'password': hashed_password
            })
            db.commit()
            
            return jsonify({'success': True, 'message': 'Cont creat cu succes'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la înregistrare: {str(e)}'}), 500

# Rute pentru rezultate
@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        with SessionLocal() as db:
            results = db.execute(text("""
                SELECT * FROM rezultate ORDER BY numar_voturi DESC
            """)).fetchall()
            
            results_list = []
            for row in results:
                results_list.append({
                    'id': row.id,
                    'nume_candidat': row.nume_candidat,
                    'partid': row.partid,
                    'numar_voturi': row.numar_voturi
                })
            
            return jsonify({'success': True, 'results': results_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la obținerea rezultatelor: {str(e)}'}), 500

# Rute pentru știri
@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        with SessionLocal() as db:
            news = db.execute(text("""
                SELECT * FROM noutati ORDER BY data_publicarii DESC
            """)).fetchall()
            
            news_list = []
            for row in news:
                news_list.append({
                    'id': row.id,
                    'titlu': row.titlu,
                    'continut': row.continut,
                    'data_publicarii': row.data_publicarii.isoformat() if row.data_publicarii else None
                })
            
            return jsonify({'success': True, 'news': news_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la obținerea știrilor: {str(e)}'}), 500

# Rute pentru votare
@app.route('/api/vote', methods=['POST'])
def vote():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        candidat_id = data.get('candidat_id')
        
        if not user_id or not candidat_id:
            return jsonify({'success': False, 'message': 'User ID și candidat ID sunt obligatorii'}), 400
        
        with SessionLocal() as db:
            # Verifică dacă utilizatorul a votat deja
            existing_vote = db.execute(text("""
                SELECT * FROM voturi WHERE user_id = :user_id
            """), {'user_id': user_id}).fetchone()
            
            if existing_vote:
                return jsonify({'success': False, 'message': 'Ați votat deja'}), 400
            
            # Înregistrează votul
            db.execute(text("""
                INSERT INTO voturi (user_id, candidat_id) 
                VALUES (:user_id, :candidat_id)
            """), {'user_id': user_id, 'candidat_id': candidat_id})
            
            # Actualizează numărul de voturi
            db.execute(text("""
                UPDATE rezultate 
                SET numar_voturi = numar_voturi + 1 
                WHERE id = :candidat_id
            """), {'candidat_id': candidat_id})
            
            db.commit()
            
            return jsonify({'success': True, 'message': 'Vot înregistrat cu succes'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la votare: {str(e)}'}), 500

# Rute admin
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    try:
        with SessionLocal() as db:
            users = db.execute(text("""
                SELECT id, username, email, idnp, is_admin, created_at 
                FROM users ORDER BY created_at DESC
            """)).fetchall()
            
            users_list = []
            for row in users:
                users_list.append({
                    'id': row.id,
                    'username': row.username,
                    'email': row.email,
                    'idnp': row.idnp,
                    'is_admin': row.is_admin,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            return jsonify({'success': True, 'users': users_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la obținerea utilizatorilor: {str(e)}'}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    try:
        with SessionLocal() as db:
            # Număr total utilizatori
            total_users = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
            
            # Număr total voturi
            total_votes = db.execute(text("SELECT COUNT(*) FROM voturi")).fetchone()[0]
            
            # Ultimele logări
            recent_logins = db.execute(text("""
                SELECT username, success, created_at 
                FROM login_logs ll
                JOIN users u ON ll.user_id = u.id
                ORDER BY ll.created_at DESC 
                LIMIT 10
            """)).fetchall()
            
            logins_list = []
            for row in recent_logins:
                logins_list.append({
                    'username': row.username,
                    'success': row.success,
                    'created_at': row.created_at.isoformat() if row.created_at else None
                })
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_votes': total_votes
                },
                'recent_logins': logins_list
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Eroare la obținerea statisticilor: {str(e)}'}), 500

# Rute pentru fișiere statice
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_client_files(filename):
    return send_from_directory(app.static_folder, filename)

# Rute speciale pentru pagini
@app.route('/login')
def serve_login():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/admin/')
def serve_admin():
    return send_from_directory(app.static_folder, 'admin/admin.html')

@app.route('/admin/<path:filename>')
def serve_admin_files(filename):
    return send_from_directory(app.static_folder, f'admin/{filename}')

@app.route('/admin')
def serve_admin_redirect():
    return send_from_directory(app.static_folder, 'admin/admin.html')

# Rută pentru testare conexiune bază date
@app.route('/api/health')
def health_check():
    if not engine:
        return jsonify({'status': 'error', 'message': 'Engine baza date negăsit'}), 500
        
    try:
        with SessionLocal() as db:
            db.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy', 
            'database': 'connected',
            'message': 'Conexiune reușită!'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'connection failed',
            'error': str(e)
        }), 500

# Rută pentru debug - verifică structura tabelelor
@app.route('/api/debug-tables')
def debug_tables():
    try:
        with SessionLocal() as db:
            # Verifică toate tabelele
            tables = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_list = [row[0] for row in tables]
            
            # Verifică coloanele pentru fiecare tabel
            tables_info = {}
            for table_name in table_list:
                columns = db.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """))
                tables_info[table_name] = [dict(row) for row in columns]
            
            return jsonify({
                "tables": table_list,
                "tables_info": tables_info
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 Pornire Voting App pe portul {port}")
    print(f"📁 Fișiere statice din: {app.static_folder}")
    print(f"🔧 Mod debug: {debug}")
    
    app.run(debug=debug, port=port, host='0.0.0.0')