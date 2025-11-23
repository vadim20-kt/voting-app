import hashlib
import random
import string
import os
from urllib.parse import urlparse

# Detectează tipul de bază de date
DB_TYPE = None
DB_CONNECTOR = None

def detect_db_type():
    """Detectează automat tipul de bază de date"""
    global DB_TYPE, DB_CONNECTOR
    
    # Verifică dacă există URL PostgreSQL (Render)
    postgres_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    if postgres_url and 'postgres' in postgres_url.lower():
        DB_TYPE = 'postgresql'
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            DB_CONNECTOR = psycopg2
            print("✓ Detectat PostgreSQL")
            return 'postgresql'
        except ImportError:
            print("⚠️ psycopg2 nu este instalat, încearcă MySQL")
    
    # Verifică dacă există URL MySQL (Heroku)
    mysql_url = os.getenv('CLEARDB_DATABASE_URL') or os.getenv('JAWSDB_URL')
    if mysql_url and 'mysql' in mysql_url.lower():
        DB_TYPE = 'mysql'
        try:
            import mysql.connector
            from mysql.connector import Error
            DB_CONNECTOR = mysql.connector
            print("✓ Detectat MySQL (Heroku)")
            return 'mysql'
        except ImportError:
            print("⚠️ mysql-connector nu este instalat")
    
    # Default: MySQL local
    DB_TYPE = 'mysql'
    try:
        import mysql.connector
        from mysql.connector import Error
        DB_CONNECTOR = mysql.connector
        print("✓ Folosind MySQL (local)")
        return 'mysql'
    except ImportError:
        # Fallback la PostgreSQL dacă MySQL nu este disponibil
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            DB_CONNECTOR = psycopg2
            DB_TYPE = 'postgresql'
            print("✓ Folosind PostgreSQL (fallback)")
            return 'postgresql'
        except ImportError:
            print("❌ Nici MySQL, nici PostgreSQL nu sunt disponibile!")
            return None

def get_db_config():
    """Obține configurația bazei de date"""
    db_type = detect_db_type()
    
    # PostgreSQL (Render)
    if db_type == 'postgresql':
        postgres_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
        if postgres_url:
            try:
                parsed = urlparse(postgres_url)
                config = {
                    'host': parsed.hostname,
                    'user': parsed.username,
                    'password': parsed.password,
                    'database': parsed.path[1:] if parsed.path else None,
                    'port': parsed.port or 5432
                }
                print(f"✓ Conectare PostgreSQL: {config['host']}")
                return ('postgresql', config)
            except Exception as e:
                print(f"⚠️ Eroare la parsarea URL-ului PostgreSQL: {e}")
        
        # Fallback la variabile de mediu
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'voting_app'),
            'port': int(os.getenv('DB_PORT', '5432'))
        }
        return ('postgresql', config)
    
    # MySQL (Heroku sau local)
    mysql_url = os.getenv('CLEARDB_DATABASE_URL') or os.getenv('JAWSDB_URL')
    if mysql_url:
        try:
            parsed = urlparse(mysql_url)
            config = {
                'host': parsed.hostname,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path[1:] if parsed.path else None,
                'port': parsed.port or 3306,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            }
            print(f"✓ Conectare MySQL: {config['host']}")
            return ('mysql', config)
        except Exception as e:
            print(f"⚠️ Eroare la parsarea URL-ului MySQL: {e}")
    
    # MySQL local
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'voting_app'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    return ('mysql', config)

def get_db_connection():
    """Creează conexiunea la baza de date"""
    db_type, config = get_db_config()
    
    try:
        if db_type == 'postgresql':
            import psycopg2
            conn = psycopg2.connect(**config)
            return ('postgresql', conn)
        else:
            import mysql.connector
            from mysql.connector import Error
            conn = mysql.connector.connect(**config)
            return ('mysql', conn)
    except Exception as e:
        print(f"Eroare la conectarea la baza de date {db_type}: {e}")
        return None

def get_db_cursor(conn_tuple, dictionary=True):
    """Creează un cursor"""
    if not conn_tuple:
        return None
    
    db_type, conn = conn_tuple
    
    if db_type == 'postgresql':
        from psycopg2.extras import RealDictCursor
        if dictionary:
            return conn.cursor(cursor_factory=RealDictCursor)
        return conn.cursor()
    else:
        if dictionary:
            return conn.cursor(dictionary=True)
        return conn.cursor()

# Funcții helper pentru compatibilitate cu codul existent
def _unwrap_connection(conn_result):
    """Extrage conexiunea din tuple pentru compatibilitate"""
    if conn_result is None:
        return None
    if isinstance(conn_result, tuple):
        return conn_result[1]  # Returnează doar conexiunea
    return conn_result

# Wrapper pentru compatibilitate - returnează doar conexiunea (pentru codul existent)
def get_db_connection_simple():
    """Wrapper care returnează doar conexiunea (pentru compatibilitate)"""
    result = get_db_connection()
    if result:
        return result[1]  # Returnează doar conexiunea
    return None

def generate_verification_code():
    """Generează un cod de verificare de 6 cifre"""
    return ''.join(random.choices(string.digits, k=6))

def init_db():
    """Inițializează baza de date cu tabelele necesare"""
    conn_tuple = get_db_connection()
    if not conn_tuple:
        print("Nu se poate conecta la baza de date")
        return
    
    db_type, conn = conn_tuple
    cursor = get_db_cursor(conn_tuple, dictionary=False)
    
    try:
        # Sintaxă diferită pentru MySQL vs PostgreSQL
        if db_type == 'postgresql':
            # PostgreSQL syntax
            auto_increment = "SERIAL"
            tinyint = "BOOLEAN"
            engine = ""
            charset = ""
            datetime_type = "TIMESTAMP"
            insert_ignore = "ON CONFLICT DO NOTHING"
            date_sub = "created_at < NOW() - INTERVAL '10 minutes'"
        else:
            # MySQL syntax
            auto_increment = "INT AUTO_INCREMENT"
            tinyint = "TINYINT(1)"
            engine = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
            charset = ""
            datetime_type = "DATETIME"
            insert_ignore = "INSERT IGNORE"
            date_sub = "created_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE)"
        
        # Tabela utilizatori
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS users (
                id {auto_increment} PRIMARY KEY,
                idnp VARCHAR(13) UNIQUE NOT NULL,
                nume VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                telefon VARCHAR(15),
                parola VARCHAR(255) NOT NULL,
                rol VARCHAR(20) DEFAULT 'voter',
                is_admin {tinyint} DEFAULT 0,
                data_inregistrare TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) {engine}
        ''')
        
        # Tabela sesiuni
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS voting_sessions (
                id {auto_increment} PRIMARY KEY,
                titlu VARCHAR(255) NOT NULL,
                descriere TEXT,
                data_inceput {datetime_type},
                data_sfarsit {datetime_type},
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) {engine}
        ''')
        
        # Tabela opțiuni
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS vote_options (
                id {auto_increment} PRIMARY KEY,
                session_id INT,
                text_optiune VARCHAR(255) NOT NULL,
                FOREIGN KEY (session_id) REFERENCES voting_sessions(id) ON DELETE CASCADE
            ) {engine}
        ''')
        
        # Tabela voturi
        if db_type == 'postgresql':
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    session_id INT,
                    option_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES voting_sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (option_id) REFERENCES vote_options(id) ON DELETE CASCADE,
                    UNIQUE (user_id, session_id)
                )
            ''')
        else:
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
        
        # Tabela coduri verificare
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id {auto_increment} PRIMARY KEY,
                idnp VARCHAR(13) NOT NULL,
                code VARCHAR(6) NOT NULL,
                used {tinyint} DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) {engine}
        ''')
        
        # Indexuri
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_idnp ON verification_codes(idnp)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_created ON verification_codes(created_at)")
        except:
            pass  # Indexurile există deja
        
        # Șterge codurile expirate
        try:
            cursor.execute(f"DELETE FROM verification_codes WHERE {date_sub}")
            conn.commit()
        except Exception as e:
            print(f"Eroare la curățarea codurilor: {e}")
        
        # Tabela loguri login
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS login_logs (
                id {auto_increment} PRIMARY KEY,
                user_id INT,
                idnp VARCHAR(13) NOT NULL,
                nume VARCHAR(100),
                email VARCHAR(100),
                ip_address VARCHAR(45),
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'success',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) {engine}
        ''')
        
        # Tabela noutăți
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS noutati (
                id {auto_increment} PRIMARY KEY,
                titlu VARCHAR(255) NOT NULL,
                continut TEXT,
                data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                autor VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active'
            ) {engine}
        ''')
        
        # Tabela rezultate
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS rezultate (
                id {auto_increment} PRIMARY KEY,
                id_sesiune INT,
                titlu VARCHAR(255) NOT NULL,
                descriere TEXT,
                total_voturi INT DEFAULT 0,
                castigator VARCHAR(255),
                data_publicarii TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_sesiune) REFERENCES voting_sessions(id) ON DELETE SET NULL
            ) {engine}
        ''')
        
        # Adaugă utilizatori demo
        admin_password = hashlib.md5('admin123'.encode()).hexdigest()
        user_password = hashlib.md5('user123'.encode()).hexdigest()
        
        if db_type == 'postgresql':
            cursor.execute('''
                INSERT INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (idnp) DO NOTHING
            ''', ('1234567890123', 'Administrator', 'admin@vote.md', admin_password, True))
            
            cursor.execute('''
                INSERT INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (idnp) DO NOTHING
            ''', ('1231231231231', 'Utilizator Demo', 'user@vote.md', user_password, False))
        else:
            cursor.execute('''
                INSERT IGNORE INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
            ''', ('1234567890123', 'Administrator', 'admin@vote.md', admin_password, 1))
            
            cursor.execute('''
                INSERT IGNORE INTO users (idnp, nume, email, parola, is_admin) 
                VALUES (%s, %s, %s, %s, %s)
            ''', ('1231231231231', 'Utilizator Demo', 'user@vote.md', user_password, 0))
        
        conn.commit()
        print(f"✅ Baza de date {db_type.upper()} este gata!")
        print("👤 Admin: IDNP=1234567890123, Parola=admin123")
        print("👤 User:  IDNP=1231231231231, Parola=user123")
        
    except Exception as e:
        print(f"✗ Eroare la crearea tabelelor: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
