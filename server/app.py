from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import hashlib
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("✓ Environment variables loaded")
except ImportError:
    logger.warning("⚠️ python-dotenv is not installed")

app = Flask(__name__)

# CORS configuration for development
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["*"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Database configuration
def get_database_url():
    # Check for Render's PostgreSQL URL first
    if 'DATABASE_URL' in os.environ:
        db_url = os.environ['DATABASE_URL']
        # Fix for Render's PostgreSQL URL format
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    # Fallback to direct URL or local development
    return os.getenv('DATABASE_URL', 'postgresql://voting_app_ldec_user:VROdX2znIac3Hk7TRE2Xzgb18axGRwqx@dpg-d4h4rvh5pdvs7390tdrg-a.frankfurt-postgres.render.com:5432/voting_app_ldec')

# Create database engine and session
DATABASE_URL = get_database_url()
logger.info(f"🔗 Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            'connect_timeout': 10,
            'options': '-c statement_timeout=10000'
        }
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Database engine created successfully")
    
    # Test the connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info("✅ Database connection test successful")
    
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {str(e)}")
    engine = None
    SessionLocal = None

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database initialization
def init_db():
    if not engine:
        logger.error("❌ Cannot initialize - database engine not available")
        return False
        
    try:
        with engine.connect() as conn:
            # Drop existing tables if they exist
            conn.execute(text("""
                DROP TABLE IF EXISTS login_logs CASCADE;
                DROP TABLE IF EXISTS voturi CASCADE;
                DROP TABLE IF EXISTS rezultate CASCADE;
                DROP TABLE IF EXISTS noutati CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
            
                -- Create all tables with correct schema
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
    idnp VARCHAR(13) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(200),
    verification_token_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
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
            
            # Add admin user if not exists
            admin_check = conn.execute(text("""
                SELECT * FROM users WHERE username = 'admin' OR idnp = '1234567890123'
            """))
            admin_exists = admin_check.fetchone()
            
            if not admin_exists:
                hashed_password = hash_password('admin123')
                conn.execute(text("""
                    INSERT INTO users (username, email, idnp, phone, password, is_admin) 
                    VALUES ('admin', 'admin@voting.com', '1234567890123', '123456789', :password, TRUE)
                """), {'password': hashed_password})
                logger.info("✅ Admin user created with IDNP: 1234567890123")
            elif admin_exists.idnp != '1234567890123':
                # Update existing admin to use the correct IDNP
                conn.execute(text("""
                    UPDATE users 
                    SET idnp = '1234567890123' 
                    WHERE username = 'admin' AND idnp != '1234567890123'
                """))
                logger.info("✅ Updated admin user with correct IDNP")
            
            # Add sample candidates
            candidates_check = conn.execute(text("SELECT * FROM rezultate"))
            if not candidates_check.fetchone():
                conn.execute(text("""
                    INSERT INTO rezultate (nume_candidat, partid, numar_voturi) 
                    VALUES 
                    ('Ion Popescu', 'Partidul Democrat', 0),
                    ('Maria Ionescu', 'Partidul Liberal', 0),
                    ('Vasile Georgescu', 'Partidul Social', 0)
                """))
                logger.info("✅ Sample candidates added")
            
            # Add sample news
            news_check = conn.execute(text("SELECT * FROM noutati"))
            if not news_check.fetchone():
                conn.execute(text("""
                    INSERT INTO noutati (titlu, continut) 
                    VALUES 
                    ('Alegeri 2024', 'Procesul electoral a început. Toți cetățenii sunt invitați să voteze.'),
                    ('Informații importante', 'Vă rugăm să vă aduceți buletinul la secția de votare.')
                """))
                logger.info("✅ Sample news added")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# Initialize database
try:
    logger.info("🌐 Initializing database...")
    if init_db():
        logger.info("✅ Database initialized successfully")
    else:
        logger.error("❌ Failed to initialize database")
except Exception as e:
    logger.error(f"❌ Error during database initialization: {str(e)}")

# Configure static files
app.static_folder = '../client'
app.static_url_path = ''

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    if not engine:
        return jsonify({'status': 'error', 'message': 'Database engine not found'}), 500
        
    try:
        with SessionLocal() as db:
            db.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy', 
            'database': 'connected',
            'message': 'Connection successful!'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'connection failed',
            'error': str(e)
        }), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        idnp = data.get('idnp')
        password = data.get('password')
        
        if not idnp or not password:
            return jsonify({'success': False, 'message': 'IDNP și parola sunt obligatorii'}), 400
        
        with SessionLocal() as db:
            user = db.execute(text("""
                SELECT * FROM users WHERE idnp = :idnp
            """), {'idnp': idnp}).fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'IDNP-ul nu există'}), 401
            
            hashed_password = hash_password(password)
            if user.password != hashed_password:
                return jsonify({'success': False, 'message': 'Parolă incorectă'}), 401
            
            # Log the login attempt
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
                'message': 'Autentificare reușită',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': user.is_admin
                }
            })
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'message': f'Eroare la autentificare: {str(e)}'}), 500

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json()
        idnp = data.get('idnp')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        
        if not all([idnp, name, email, password]):
            return jsonify({
                'success': False, 
                'message': 'Toate câmpurile marcate cu * sunt obligatorii'
            }), 400
        
        with SessionLocal() as db:
            existing_user = db.execute(text("""
                SELECT * FROM users WHERE idnp = :idnp OR email = :email
            """), {'idnp': idnp, 'email': email}).fetchone()
            
            if existing_user:
                return jsonify({
                    'success': False, 
                    'message': 'Acest IDNP sau adresă de email este deja înregistrat'
                }), 400
            
            hashed_password = hash_password(password)
            db.execute(text("""
                INSERT INTO users (username, email, idnp, phone, password) 
                VALUES (:username, :email, :idnp, :phone, :password)
            """), {
                'username': name,
                'email': email,
                'idnp': idnp,
                'phone': phone,
                'password': hashed_password
            })
            db.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Cont creat cu succes! Vă puteți autentifica acum.'
            })
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Eroare la înregistrare: {str(e)}'
        }), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        with SessionLocal() as db:
            results = db.execute(text("""
                SELECT * FROM rezultate ORDER BY numar_voturi DESC
            """)).fetchall()
            
            results_list = [{
                'id': row.id,
                'nume_candidat': row.nume_candidat,
                'partid': row.partid,
                'numar_voturi': row.numar_voturi
            } for row in results]
            
            return jsonify({'success': True, 'results': results_list})
    except Exception as e:
        logger.error(f"Get results error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Eroare la obținerea rezultatelor: {str(e)}'
        }), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        with SessionLocal() as db:
            news = db.execute(text("""
                SELECT * FROM noutati ORDER BY data_publicarii DESC
            """)).fetchall()
            
            news_list = [{
                'id': row.id,
                'titlu': row.titlu,
                'continut': row.continut,
                'data_publicarii': row.data_publicarii.isoformat() if row.data_publicarii else None
            } for row in news]
            
            return jsonify({'success': True, 'news': news_list})
    except Exception as e:
        logger.error(f"Get news error: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'Eroare la obținerea știrilor: {str(e)}'
        }), 500

@app.route('/api/vote', methods=['POST', 'OPTIONS'])
def vote():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

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
        logger.error(f"Vote error: {str(e)}")
        return jsonify({'success': False, 'message': f'Eroare la votare: {str(e)}'}), 500

# Admin routes
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    try:
        with SessionLocal() as db:
            users = db.execute(text("""
                SELECT id, username, email, idnp, phone, is_admin, created_at 
                FROM users ORDER BY created_at DESC
            """)).fetchall()
            
            users_list = [{
                'id': row.id,
                'username': row.username,
                'email': row.email,
                'idnp': row.idnp,
                'phone': row.phone,
                'is_admin': row.is_admin,
                'created_at': row.created_at.isoformat() if row.created_at else None
            } for row in users]
            
            return jsonify({'success': True, 'users': users_list})
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
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
                SELECT u.username, ll.success, ll.created_at 
                FROM login_logs ll
                JOIN users u ON ll.user_id = u.id
                ORDER BY ll.created_at DESC 
                LIMIT 10
            """)).fetchall()
            
            logins_list = [{
                'username': row.username,
                'success': row.success,
                'created_at': row.created_at.isoformat() if row.created_at else None
            } for row in recent_logins]
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_votes': total_votes
                },
                'recent_logins': logins_list
            })
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({'success': False, 'message': f'Eroare la obținerea statisticilor: {str(e)}'}), 500

# Static file routes
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_client_files(filename):
    return send_from_directory(app.static_folder, filename)

# Special routes for pages
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

# Debug route - check table structure
@app.route('/api/debug-tables')
def debug_tables():
    try:
        with SessionLocal() as db:
            # Check all tables
            tables = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_list = [row[0] for row in tables]
            
            # Check columns for each table
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
    
    logger.info(f"🚀 Starting Voting App on port {port}")
    logger.info(f"📁 Static files from: {app.static_folder}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, port=port, host='0.0.0.0')