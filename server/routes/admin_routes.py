from flask import Blueprint, request, jsonify
from utils.database import get_db_connection
import hashlib

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total utilizatori
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Actualizează automat statusul sesiunilor expirate
        cursor.execute("""
            UPDATE voting_sessions 
            SET status = 'completed' 
            WHERE status = 'active' 
            AND data_sfarsit IS NOT NULL 
            AND data_sfarsit < NOW()
        """)
        conn.commit()
        
        # Total sesiuni active (doar cele care sunt în intervalul de timp corect)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM voting_sessions 
            WHERE status = 'active'
            AND (data_inceput IS NULL OR data_inceput <= NOW())
            AND (data_sfarsit IS NULL OR data_sfarsit >= NOW())
        """)
        active_sessions = cursor.fetchone()['count']
        
        # Total voturi
        cursor.execute("SELECT COUNT(*) as count FROM votes")
        total_votes = cursor.fetchone()['count']
        
        # Voturi astăzi
        cursor.execute("SELECT COUNT(*) as count FROM votes WHERE DATE(created_at) = CURDATE()")
        today_votes_result = cursor.fetchone()
        today_votes = today_votes_result['count'] if today_votes_result else 0
        
        # Total noutăți
        cursor.execute("SELECT COUNT(*) as count FROM noutati")
        total_news = cursor.fetchone()['count']
        
        # Noutăți active
        cursor.execute("SELECT COUNT(*) as count FROM noutati WHERE status = 'active' OR status IS NULL")
        active_news = cursor.fetchone()['count']
        
        # Total rezultate
        cursor.execute("SELECT COUNT(*) as count FROM rezultate")
        total_results = cursor.fetchone()['count']
        
        return jsonify({
            'total_users': total_users,
            'active_sessions': active_sessions,
            'total_votes': total_votes,
            'today_votes': today_votes,
            'total_news': total_news,
            'active_news': active_news,
            'total_results': total_results
        })
        
    except Exception as e:
        print(f"Eroare stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'total_users': 0,
            'active_sessions': 0,
            'total_votes': 0,
            'today_votes': 0,
            'total_news': 0,
            'active_news': 0,
            'total_results': 0
        }), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, idnp, nume, email, telefon, is_admin, data_inregistrare 
            FROM users 
            ORDER BY data_inregistrare DESC
        """)
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'idnp': user['idnp'],
                'nume': user['nume'],
                'email': user['email'],
                'telefon': user['telefon'],
                'is_admin': bool(user['is_admin']),
                'data_inregistrare': str(user['data_inregistrare']) if user['data_inregistrare'] else None
            })
        
        return jsonify(users_list)
        
    except Exception as e:
        print(f"Eroare users: {e}")
        return jsonify([]), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/sessions', methods=['GET'])
def get_sessions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        
        # Actualizează sesiunile care au început dar nu au status corect
        cursor.execute("""
            UPDATE voting_sessions 
            SET status = 'active' 
            WHERE status = 'pending' 
            AND data_inceput IS NOT NULL 
            AND data_inceput <= NOW()
            AND (data_sfarsit IS NULL OR data_sfarsit >= NOW())
        """)
        conn.commit()
        
        cursor.execute("""
            SELECT vs.id, vs.titlu, vs.descriere, vs.data_inceput, 
                   vs.data_sfarsit, vs.status, vs.created_at,
                   COUNT(vo.id) as options_count
            FROM voting_sessions vs
            LEFT JOIN vote_options vo ON vs.id = vo.session_id
            GROUP BY vs.id
            ORDER BY vs.created_at DESC
        """)
        sessions = cursor.fetchall()
        
        sessions_list = []
        for session in sessions:
            sessions_list.append({
                'id': session['id'],
                'titlu': session['titlu'],
                'descriere': session['descriere'],
                'data_inceput': str(session['data_inceput']) if session['data_inceput'] else None,
                'data_sfarsit': str(session['data_sfarsit']) if session['data_sfarsit'] else None,
                'status': session['status'],
                'created_at': str(session['created_at']) if session['created_at'] else None,
                'options_count': session['options_count']
            })
        
        return jsonify(sessions_list)
        
    except Exception as e:
        print(f"Eroare sessions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/sessions', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        descriere = data.get('descriere')
        options = data.get('options', [])
        status = data.get('status', 'active')
        data_inceput = data.get('data_inceput')
        data_sfarsit = data.get('data_sfarsit')
        
        if not titlu:
            return jsonify({'success': False, 'error': 'Titlul sesiunii este obligatoriu'}), 400
        
        if not options or len(options) < 2:
            return jsonify({'success': False, 'error': 'Sunt necesare cel puțin 2 opțiuni de vot'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Crează sesiunea
        cursor.execute("""
            INSERT INTO voting_sessions (titlu, descriere, status, data_inceput, data_sfarsit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (titlu, descriere, status, data_inceput, data_sfarsit))
        
        session_id = cursor.lastrowid
        
        # Adaugă opțiunile de vot
        for option_text in options:
            if option_text.strip():
                cursor.execute("""
                    INSERT INTO vote_options (session_id, text_optiune) 
                    VALUES (%s, %s)
                """, (session_id, option_text.strip()))
        
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Sesiune creată cu succes',
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Eroare create session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă sesiunea există
        cursor.execute("SELECT id FROM voting_sessions WHERE id = %s", (session_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Sesiunea nu există'}), 404
        
        # Șterge voturile asociate
        cursor.execute("DELETE FROM votes WHERE session_id = %s", (session_id,))
        
        # Șterge opțiunile de vot
        cursor.execute("DELETE FROM vote_options WHERE session_id = %s", (session_id,))
        
        # Șterge sesiunea
        cursor.execute("DELETE FROM voting_sessions WHERE id = %s", (session_id,))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Sesiune ștearsă cu succes'})
        
    except Exception as e:
        print(f"Eroare delete session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/sessions/<int:session_id>/results', methods=['GET'])
def get_session_results(session_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă sesiunea există
        cursor.execute("SELECT titlu FROM voting_sessions WHERE id = %s", (session_id,))
        session = cursor.fetchone()
        if not session:
            return jsonify({'success': False, 'error': 'Sesiunea nu există'}), 404
        
        # Obține rezultatele voturilor
        cursor.execute("""
            SELECT vo.text_optiune, COUNT(v.id) as vote_count
            FROM vote_options vo
            LEFT JOIN votes v ON vo.id = v.option_id
            WHERE vo.session_id = %s
            GROUP BY vo.id
            ORDER BY vote_count DESC
        """, (session_id,))
        
        results = cursor.fetchall()
        
        # Total voturi
        cursor.execute("SELECT COUNT(*) as total FROM votes WHERE session_id = %s", (session_id,))
        total_votes = cursor.fetchone()['total']
        
        results_list = []
        for result in results:
            percentage = (result['vote_count'] / total_votes * 100) if total_votes > 0 else 0
            results_list.append({
                'option': result['text_optiune'],
                'votes': result['vote_count'],
                'percentage': round(percentage, 2)
            })
        
        return jsonify({
            'success': True,
            'session_title': session['titlu'],
            'total_votes': total_votes,
            'results': results_list
        })
        
    except Exception as e:
        print(f"Eroare results: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă utilizatorul există
        cursor.execute("SELECT id, is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'success': False, 'error': 'Utilizatorul nu există'}), 404
        
        # Nu permite ștergerea conturilor admin
        if user['is_admin']:
            return jsonify({'success': False, 'error': 'Nu poți șterge conturi de administrator'}), 403
        
        # Șterge voturile utilizatorului
        cursor.execute("DELETE FROM votes WHERE user_id = %s", (user_id,))
        
        # Șterge codurile de verificare
        cursor.execute("DELETE FROM verification_codes WHERE idnp = (SELECT idnp FROM users WHERE id = %s)", (user_id,))
        
        # Șterge utilizatorul
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Utilizator șters cu succes'})
        
    except Exception as e:
        print(f"Eroare delete user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ===== RUTE PENTRU NOUTĂȚI =====
@admin_bp.route('/news', methods=['GET'])
def get_news():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM noutati 
            ORDER BY data_publicarii DESC
        """)
        news = cursor.fetchall()
        
        return jsonify(news)
    except Exception as e:
        print(f"Eroare get news: {e}")
        return jsonify([]), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/news', methods=['POST'])
def create_news():
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        continut = data.get('continut', '')
        autor = data.get('autor', 'Administrator')
        
        if not titlu:
            return jsonify({'success': False, 'error': 'Titlul este obligatoriu'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Asigură-te că data_publicarii este setată explicit
        from datetime import datetime
        cursor.execute("""
            INSERT INTO noutati (titlu, continut, autor, data_publicarii) 
            VALUES (%s, %s, %s, NOW())
        """, (titlu, continut, autor))
        
        conn.commit()
        news_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message': 'Noutate creată cu succes',
            'id': news_id
        })
    except Exception as e:
        print(f"Eroare create news: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/news/<int:news_id>', methods=['PUT'])
def update_news(news_id):
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        continut = data.get('continut', '')
        autor = data.get('autor')
        status = data.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă noutatea există
        cursor.execute("SELECT id FROM noutati WHERE id = %s", (news_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Noutatea nu există'}), 404
        
        # Actualizează
        updates = []
        values = []
        
        if titlu:
            updates.append("titlu = %s")
            values.append(titlu)
        if continut is not None:
            updates.append("continut = %s")
            values.append(continut)
        if autor:
            updates.append("autor = %s")
            values.append(autor)
        if status:
            updates.append("status = %s")
            values.append(status)
        
        if updates:
            values.append(news_id)
            cursor.execute(f"""
                UPDATE noutati 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Noutate actualizată cu succes'})
    except Exception as e:
        print(f"Eroare update news: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("DELETE FROM noutati WHERE id = %s", (news_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Noutate ștearsă cu succes'})
    except Exception as e:
        print(f"Eroare delete news: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ===== RUTE PENTRU REZULTATE =====
@admin_bp.route('/results', methods=['GET'])
def get_results():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT r.*, vs.titlu as session_titlu
            FROM rezultate r
            LEFT JOIN voting_sessions vs ON r.id_sesiune = vs.id
            ORDER BY r.data_publicarii DESC
        """)
        results = cursor.fetchall()
        
        return jsonify(results)
    except Exception as e:
        print(f"Eroare get results: {e}")
        return jsonify([]), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/results', methods=['POST'])
def create_result():
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        descriere = data.get('descriere', '')
        id_sesiune = data.get('id_sesiune')
        total_voturi = data.get('total_voturi', 0)
        castigator = data.get('castigator', '')
        
        if not titlu:
            return jsonify({'success': False, 'error': 'Titlul este obligatoriu'}), 400
        
        # Convertim id_sesiune la None dacă este string gol sau 0
        if id_sesiune == '' or id_sesiune == 0:
            id_sesiune = None
        elif id_sesiune:
            id_sesiune = int(id_sesiune)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        print(f"📝 Creare rezultat: titlu={titlu}, id_sesiune={id_sesiune}, total_voturi={total_voturi}")
        
        cursor.execute("""
            INSERT INTO rezultate (titlu, descriere, id_sesiune, total_voturi, castigator) 
            VALUES (%s, %s, %s, %s, %s)
        """, (titlu, descriere, id_sesiune, total_voturi, castigator))
        
        conn.commit()
        result_id = cursor.lastrowid
        
        print(f"✅ Rezultat creat cu succes, ID: {result_id}")
        
        return jsonify({
            'success': True,
            'message': 'Rezultat creat cu succes',
            'id': result_id
        })
    except Exception as e:
        print(f"❌ Eroare create result: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/results/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        descriere = data.get('descriere')
        id_sesiune = data.get('id_sesiune')
        total_voturi = data.get('total_voturi')
        castigator = data.get('castigator')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă rezultatul există
        cursor.execute("SELECT id FROM rezultate WHERE id = %s", (result_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Rezultatul nu există'}), 404
        
        # Actualizează
        updates = []
        values = []
        
        if titlu:
            updates.append("titlu = %s")
            values.append(titlu)
        if descriere is not None:
            updates.append("descriere = %s")
            values.append(descriere)
        if id_sesiune is not None:
            updates.append("id_sesiune = %s")
            values.append(id_sesiune)
        if total_voturi is not None:
            updates.append("total_voturi = %s")
            values.append(total_voturi)
        if castigator is not None:
            updates.append("castigator = %s")
            values.append(castigator)
        
        if updates:
            values.append(result_id)
            cursor.execute(f"""
                UPDATE rezultate 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Rezultat actualizat cu succes'})
    except Exception as e:
        print(f"Eroare update result: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@admin_bp.route('/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("DELETE FROM rezultate WHERE id = %s", (result_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Rezultat șters cu succes'})
    except Exception as e:
        print(f"Eroare delete result: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ===== RUTĂ PENTRU EDITARE SESIUNE =====
@admin_bp.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    try:
        data = request.get_json()
        titlu = data.get('titlu')
        descriere = data.get('descriere')
        status = data.get('status')
        data_inceput = data.get('data_inceput')
        data_sfarsit = data.get('data_sfarsit')
        options = data.get('options')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verifică dacă sesiunea există
        cursor.execute("SELECT id FROM voting_sessions WHERE id = %s", (session_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Sesiunea nu există'}), 404
        
        # Actualizează sesiunea
        updates = []
        values = []
        
        if titlu:
            updates.append("titlu = %s")
            values.append(titlu)
        if descriere is not None:
            updates.append("descriere = %s")
            values.append(descriere)
        if status:
            updates.append("status = %s")
            values.append(status)
        if data_inceput:
            updates.append("data_inceput = %s")
            values.append(data_inceput)
        if data_sfarsit:
            updates.append("data_sfarsit = %s")
            values.append(data_sfarsit)
        
        if updates:
            values.append(session_id)
            cursor.execute(f"""
                UPDATE voting_sessions 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
        
        # Actualizează opțiunile dacă sunt furnizate
        if options is not None:
            # Șterge opțiunile vechi
            cursor.execute("DELETE FROM vote_options WHERE session_id = %s", (session_id,))
            
            # Adaugă opțiunile noi
            for option_text in options:
                if option_text.strip():
                    cursor.execute("""
                        INSERT INTO vote_options (session_id, text_optiune) 
                        VALUES (%s, %s)
                    """, (session_id, option_text.strip()))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Sesiune actualizată cu succes'})
    except Exception as e:
        print(f"Eroare update session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()