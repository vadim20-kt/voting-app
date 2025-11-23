from flask import Blueprint, request, jsonify
from utils.database import get_db_connection, get_db_cursor
import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api')

# Noutăți
@user_bp.route('/news', methods=['GET'])
def get_news():
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    cursor.execute('SELECT * FROM noutati ORDER BY data_publicarii DESC')
    news = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(news)

# Rezultate anterioare
@user_bp.route('/results', methods=['GET'])
def get_results():
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    cursor.execute('''
        SELECT r.*, vs.titlu as session_titlu
        FROM rezultate r 
        LEFT JOIN voting_sessions vs ON r.id_sesiune = vs.id 
        ORDER BY r.id DESC
    ''')
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

# Sesiuni active
@user_bp.route('/sessions/active', methods=['GET'])
def get_active_sessions():
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    
    # Actualizează automat statusul sesiunilor expirate
    cursor.execute("""
        UPDATE voting_sessions 
        SET status = 'completed' 
        WHERE status = 'active' 
        AND data_sfarsit IS NOT NULL 
        AND data_sfarsit < NOW()
    """)
    conn.commit()
    
    # Actualizează sesiunile care nu au început încă
    cursor.execute("""
        UPDATE voting_sessions 
        SET status = 'pending' 
        WHERE status = 'active' 
        AND data_inceput IS NOT NULL 
        AND data_inceput > NOW()
    """)
    conn.commit()
    
    # Obține doar sesiunile active (status = 'active' și în intervalul de timp corect)
    cursor.execute('''
        SELECT vs.*, COUNT(vo.id) as num_options 
        FROM voting_sessions vs 
        LEFT JOIN vote_options vo ON vs.id = vo.session_id 
        WHERE vs.status = 'active'
        AND (vs.data_inceput IS NULL OR vs.data_inceput <= NOW())
        AND (vs.data_sfarsit IS NULL OR vs.data_sfarsit >= NOW())
        GROUP BY vs.id
        ORDER BY vs.created_at DESC
    ''')
    sessions = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sessions)

# Detalii sesiune
@user_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    cursor.execute('SELECT * FROM voting_sessions WHERE id = %s', (session_id,))
    session = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not session:
        return jsonify({'error': 'Sesiunea nu există'}), 404
    
    return jsonify(session)

# Opțiuni pentru sesiune
@user_bp.route('/sessions/<int:session_id>/options', methods=['GET'])
def get_session_options(session_id):
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    cursor.execute('SELECT * FROM vote_options WHERE session_id = %s', (session_id,))
    options = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(options)

# Trimitere vot
@user_bp.route('/vote', methods=['POST'])
def submit_vote():
    data = request.json
    user_id = data.get('user_id')
    option_id = data.get('option_id')
    
    if not user_id or not option_id:
        return jsonify({'error': 'user_id și option_id sunt obligatorii'}), 400
    
    conn_result = get_db_connection()
    if not conn_result:
        return jsonify({'error': 'Database connection failed'}), 500
    
    db_type, conn = conn_result
    cursor = get_db_cursor(conn_result, dictionary=True)
    
    try:
        # Verifică dacă utilizatorul a votat deja în această sesiune
        cursor.execute('''
            SELECT v.* FROM votes v 
            JOIN vote_options vo ON v.option_id = vo.id 
            WHERE v.user_id = %s AND vo.session_id = (
                SELECT session_id FROM vote_options WHERE id = %s
            )
        ''', (user_id, option_id))
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Ați votat deja în această sesiune'}), 400
        
        # Obține session_id pentru opțiune
        cursor.execute('SELECT session_id FROM vote_options WHERE id = %s', (option_id,))
        option_data = cursor.fetchone()
        
        if not option_data:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Opțiunea nu există'}), 404
        
        session_id = option_data['session_id']
        
        # Inserează votul
        cursor.execute('''
            INSERT INTO votes (user_id, session_id, option_id) 
            VALUES (%s, %s, %s)
        ''', (user_id, session_id, option_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Vot înregistrat cu succes'})
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({'error': f'Eroare la înregistrarea votului: {str(e)}'}), 500
