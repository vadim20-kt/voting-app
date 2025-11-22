import mysql.connector
from mysql.connector import Error
import hashlib
import random
import string
import os
from urllib.parse import urlparse

def get_db_config():
    """Obține configurația bazei de date din variabile de mediu sau default"""
    # Verifică dacă suntem pe Heroku (CLEARDB sau JAWSDB)
    db_url = os.getenv('CLEARDB_DATABASE_URL') or os.getenv('JAWSDB_URL')
    
    if db_url:
        # Parsează URL-ul Heroku (format: mysql://user:pass@host:port/dbname)
        try:
            parsed = urlparse(db_url)
            config = {
                'host': parsed.hostname,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path[1:] if parsed.path else None,  # Elimină '/' din față
                'port': parsed.port or 3306,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            }
            print(f"✓ Conectare la baza de date Heroku: {config['host']}")
            return config
        except Exception as e:
            print(f"⚠️ Eroare la parsarea URL-ului DB: {e}")
    
    # Configurație locală sau din variabile de mediu
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'voting_app'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    return config

def get_db_connection():
    """Creează conexiunea la baza de date MySQL"""
    try:
        config = get_db_config()
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        print(f"Eroare la conectarea la baza de date MySQL: {e}")
        return None

def get_db_cursor(conn, dictionary=True):
    """Creează un cursor cu opțiunea de a returna dicționare"""
    if dictionary:
        return conn.cursor(dictionary=True)
    return conn.cursor()

def generate_verification_code():
    """Generează un cod de verificare de 6 cifre"""
    return ''.join(random.choices(string.digits, k=6))

def init_db():
    """Inițializează baza de date cu tabelele necesare"""
    conn = get_db_connection()
    if not conn:
        print("Nu se poate conecta la baza de date")
        return
    
    cursor = conn.cursor()
    
    try:
        # Tabela utilizatori (users)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                idnp VARCHAR(13) UNIQUE NOT NULL,
                nume VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telefon VARCHAR(15),
                parola VARCHAR(255) NOT NULL,
                rol VARCHAR(20) DEFAULT 'voter',
                is_admin TINYINT(1) DEFAULT 0,
                data_inregistrare TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabela sesiuni de vot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voting_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titlu VARCHAR(255) NOT NULL,
                descriere TEXT,
                data_inceput DATETIME,
                data_sfarsit DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabela opțiuni de vot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vote_options (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT,
                text_optiune VARCHAR(255) NOT NULL,
                FOREIGN KEY (session_id) REFERENCES voting_sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabela voturi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                session_id INT,
                option_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES voting_sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (option_id) REFERENCES vote_options(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_session (user_id, session_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabela pentru coduri de verificare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                idnp VARCHAR(13) NOT NULL,
                code VARCHAR(6) NOT NULL,
                used TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_idnp (idnp),
                INDEX idx_created (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Șterge codurile expirate (mai vechi de 10 minute)
        try:
            cursor.execute("DELETE FROM verification_codes WHERE created_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE)")
            conn.commit()
        except Exception as e:
            print(f"Eroare la curățarea codurilor expirate: {e}")
        
        # Tabela pentru loguri de login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                idnp VARCHAR(13) NOT NULL,
                nume VARCHAR(100),
                email VARCHAR(100),
                ip_address VARCHAR(45),
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'success',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Tabela pentru noutăți
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS noutati (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titlu VARCHAR(255) NOT NULL,
                continut TEXT,
                data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                autor VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Verifică și adaugă coloanele lipsă în tabela noutati (pentru tabele existente)
        try:
            # Verifică dacă coloana 'autor' există
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'noutati' 
                AND COLUMN_NAME = 'autor'
            """)
            result = cursor.fetchone()
            if result and result[0] == 0:
                # Adaugă coloana 'autor'
                cursor.execute("ALTER TABLE noutati ADD COLUMN autor VARCHAR(100) AFTER continut")
                print("✓ Coloana 'autor' adăugată în tabela noutati")
        except Exception as e:
            print(f"Eroare la verificarea coloanei 'autor': {e}")
        
        try:
            # Verifică dacă coloana 'status' există
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'noutati' 
                AND COLUMN_NAME = 'status'
            """)
            result = cursor.fetchone()
            if result and result[0] == 0:
                # Adaugă coloana 'status'
                cursor.execute("ALTER TABLE noutati ADD COLUMN status VARCHAR(20) DEFAULT 'active' AFTER autor")
                print("✓ Coloana 'status' adăugată în tabela noutati")
        except Exception as e:
            print(f"Eroare la verificarea coloanei 'status': {e}")
        
        # Tabela pentru rezultate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rezultate (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_sesiune INT,
                titlu VARCHAR(255) NOT NULL,
                descriere TEXT,
                total_voturi INT DEFAULT 0,
                castigator VARCHAR(255),
                data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_sesiune) REFERENCES voting_sessions(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        
        # Adaugă utilizator admin implicit (dacă nu există)
        admin_password = hashlib.md5('admin123'.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT IGNORE INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
            ''', ('1234567890123', 'Administrator', 'admin@vote.md', admin_password, 1))
        except Error:
            pass  # Userul există deja
        
        # Adaugă utilizator demo pentru testare
        user_password = hashlib.md5('user123'.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT IGNORE INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
            ''', ('1231231231231', 'Utilizator Demo', 'user@vote.md', user_password, 0))
        except Error:
            pass  # Userul există deja
        
        conn.commit()
        print("✅ Baza de date MySQL este gata!")
        print("👤 Admin: IDNP=1234567890123, Parola=admin123")
        print("👤 User:  IDNP=1231231231231, Parola=user123")
        
    except Error as e:
        print(f"✗ Eroare la crearea tabelelor: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
