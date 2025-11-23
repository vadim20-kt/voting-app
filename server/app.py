from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

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
            
            print("✅ Toate tabelele verificate/create")
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

# Importă și înregistrează blueprint-uri
try:
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp  
    from routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api')
    print("✅ Blueprint-uri înregistrate")
except Exception as e:
    print(f"⚠️ Eroare înregistrare blueprint-uri: {e}")

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