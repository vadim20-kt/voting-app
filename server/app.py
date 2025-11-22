from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Încarcă variabilele de mediu din .env (dacă există)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Variabile de mediu încărcate din .env")
except ImportError:
    print("⚠️ python-dotenv nu este instalat. Folosește variabile de mediu sistem sau instalează: pip install python-dotenv")

app = Flask(__name__)
CORS(app)

# Configurare pentru fișiere statice
app.static_folder = '../client'
app.static_url_path = ''

# Importă și inițializează baza de date
try:
    from utils.database import init_db
    init_db()
    print("✓ Baza de date inițializată cu succes")
except Exception as e:
    print(f"✗ Eroare la inițializarea bazei de date: {e}")

# Înregistrează blueprint-urile API
try:
    from routes.auth_routes import auth_bp
    from routes.admin_routes import admin_bp  
    from routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api')
    print("✓ Blueprint-uri înregistrate cu succes")
except Exception as e:
    print(f"✗ Eroare la înregistrarea blueprint-urilor: {e}")

# Rute pentru fișierele statice
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

# Rute pentru orice altă pagină din folderul admin
@app.route('/admin')
def serve_admin_redirect():
    return send_from_directory(app.static_folder, 'admin/admin.html')

if __name__ == '__main__':
    # Verifică dacă suntem pe Heroku sau local
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"🚀 Starting Voting App on port {port}")
    print(f"📁 Static files from: ../client")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(debug=debug, port=port, host='0.0.0.0')