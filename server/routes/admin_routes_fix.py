# Script pentru a adăuga verificări cursor în admin_routes.py
# Rulează acest script pentru a adăuga automat verificările

import re

# Citește fișierul
with open('admin_routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern pentru a găsi cursor = get_db_cursor(...) urmat de cursor.execute
pattern = r'(cursor = get_db_cursor\(conn_result, dictionary=True\))\s*\n(\s*)(cursor\.execute)'

# Înlocuiește cu verificare
replacement = r'\1\n\2if not cursor:\n\2    return jsonify({\'error\': \'Failed to create cursor\'}), 500\n\2\n\2\3'

new_content = re.sub(pattern, replacement, content)

# Salvează
with open('admin_routes.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Verificări adăugate!")


